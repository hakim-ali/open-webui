import { EventSourceParserStream } from 'eventsource-parser/stream';
import type { ParsedEvent } from 'eventsource-parser';

type TextStreamUpdate = {
	done: boolean;
	value: string;
	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	sources?: any;
	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	selectedModelId?: any;
	error?: any;
	usage?: ResponseUsage;
};

type ResponseUsage = {
	/** Including images and tools if any */
	prompt_tokens: number;
	/** The tokens generated */
	completion_tokens: number;
	/** Sum of the above two fields */
	total_tokens: number;
	/** Any other fields that aren't part of the base OpenAI spec */
	[other: string]: unknown;
};

// createOpenAITextStream takes a responseBody with a SSE response,
// and returns an async generator that emits delta updates with large deltas chunked into random sized chunks
export async function createOpenAITextStream(
	responseBody: ReadableStream<Uint8Array>,
	splitLargeDeltas: boolean
): Promise<AsyncGenerator<TextStreamUpdate>> {
	const eventStream = responseBody
		.pipeThrough(new TextDecoderStream())
		.pipeThrough(new EventSourceParserStream())
		.getReader();
	
	const iterator = openAIStreamToIterator(eventStream);
	
	if (splitLargeDeltas) {
		return streamLargeDeltasAsRandomChunks(iterator);
	}
	
	// Wrap the iterator with timeout protection
	return (async function* () {
		try {
			for await (const update of iterator) {
				yield update;
			}
		} catch (error) {
			if (error instanceof Error && error.message === 'Streaming timeout after 5 minutes') {
				console.warn('Streaming: Timeout reached, ending stream');
				yield { done: true, value: '' };
			} else {
				throw error;
			}
		}
	})();
}

async function* openAIStreamToIterator(
	reader: ReadableStreamDefaultReader<ParsedEvent>
): AsyncGenerator<TextStreamUpdate> {
	while (true) {
		const { value, done } = await reader.read();
		if (done) {
			yield { done: true, value: '' };
			break;
		}
		if (!value) {
			continue;
		}
		const data = value.data;
		if (data.startsWith('[DONE]')) {
			yield { done: true, value: '' };
			break;
		}

		try {
			const parsedData = JSON.parse(data);
			console.log(parsedData);

			if (parsedData.error) {
				yield { done: true, value: '', error: parsedData.error };
				break;
			}

			if (parsedData.sources) {
				yield { done: false, value: '', sources: parsedData.sources };
				continue;
			}

			if (parsedData.selected_model_id) {
				yield { done: false, value: '', selectedModelId: parsedData.selected_model_id };
				continue;
			}

			if (parsedData.usage) {
				yield { done: false, value: '', usage: parsedData.usage };
				continue;
			}

			yield {
				done: false,
				value: parsedData.choices?.[0]?.delta?.content ?? ''
			};
		} catch (e) {
			console.error('Error extracting delta from SSE event:', e);
		}
	}
}

// streamLargeDeltasAsRandomChunks will chunk large deltas with adaptive sizing based on content type
// This is to simulate a more fluid streaming, similar to ChatGPT's smooth experience
async function* streamLargeDeltasAsRandomChunks(
	iterator: AsyncGenerator<TextStreamUpdate>
): AsyncGenerator<TextStreamUpdate> {
	let accumulatedContent = '';
	let chunkCount = 0;
	const maxChunks = 50000; // Safety limit to prevent infinite loops
	
	for await (const textStreamUpdate of iterator) {
		if (textStreamUpdate.done) {
			yield textStreamUpdate;
			return;
		}

		if (textStreamUpdate.error) {
			yield textStreamUpdate;
			continue;
		}
		if (textStreamUpdate.sources) {
			yield textStreamUpdate;
			continue;
		}
		if (textStreamUpdate.selectedModelId) {
			yield textStreamUpdate;
			continue;
		}
		if (textStreamUpdate.usage) {
			yield textStreamUpdate;
			continue;
		}

		let content = textStreamUpdate.value;
		accumulatedContent += content;
		chunkCount++;
		
		// Safety check to prevent infinite loops
		if (chunkCount > maxChunks) {
			console.warn(`Streaming: Hit maximum chunk limit (${maxChunks}), sending remaining content as single chunk`);
			yield { done: false, value: content };
			continue;
		}
		
		// Check if we're dealing with a heading or content under a heading
		const isHeading = /^#+\s/.test(accumulatedContent);
		
		// Check if we're under a heading by looking for the last heading in accumulated content
		let isUnderHeading = false;
		const lines = accumulatedContent.split('\n');
		for (let i = lines.length - 1; i >= 0; i--) {
			const line = lines[i].trim();
			if (line.startsWith('#')) {
				isUnderHeading = true;
				break;
			} else if (line === '') {
				continue;
			} else {
				break;
			}
		}
		
		// Handle very small content chunks
		if (content.length < 3) {
			yield { done: false, value: content };
			continue;
		}
		
		// For very large content, use more aggressive chunking to prevent streaming issues
		const isLargeContent = content.length > 1000;
		const isUltraLargeContent = content.length > 5000;
		
		try {
			while (content != '') {
				// Adaptive chunk size based on content type and size
				let chunkSize;
				let delay;
				
				if (isUltraLargeContent) {
					// For ultra-large content, use very large chunks and minimal delays for maximum speed
					chunkSize = Math.min(Math.floor(Math.random() * 8) + 8, content.length); // 8-15 chars for ultra-large content
					delay = 2; // Ultra-fast speed for very large content
				} else if (isLargeContent) {
					// For large content, use larger chunks and faster streaming for speed
					chunkSize = Math.min(Math.floor(Math.random() * 4) + 4, content.length); // 4-7 chars for large content
					delay = 5; // Much faster speed for large content
				} else if (isHeading) {
					chunkSize = Math.min(Math.floor(Math.random() * 3) + 3, content.length); // 3-5 chars for headings
					delay = 25; // Slower speed for headings
				} else if (isUnderHeading) {
					chunkSize = Math.min(Math.floor(Math.random() * 4) + 5, content.length); // 5-8 chars for content under headings
					delay = 15; // Slower for content under headings
				} else {
					chunkSize = Math.min(Math.floor(Math.random() * 3) + 3, content.length); // 3-5 chars for regular content
					delay = 25; // Slower speed for regular content
				}
				
				const chunk = content.slice(0, chunkSize);
				yield { done: false, value: chunk };
				
				// Do not sleep if the tab is hidden
				// Timers are throttled to 1s in hidden tabs
				if (document?.visibilityState !== 'hidden') {
					await sleep(delay);
				}
				content = content.slice(chunkSize);
			}
		} catch (error) {
			console.error('Streaming: Error during chunk processing:', error);
			// Send the remaining content as a single chunk to prevent streaming from stopping
			if (content) {
				yield { done: false, value: content };
			}
		}
	}
}

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));
