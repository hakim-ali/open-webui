/**
 * Utility for handling external links with warning modal
 */

export interface ExternalLinkHandler {
	handleExternalLinkClick: (e: Event, url: string) => void;
	showExternalWarning: boolean;
	externalUrl: string;
	setShowExternalWarning: (show: boolean) => void;
	setExternalUrl: (url: string) => void;
}

/**
 * Creates an external link handler for components
 * @returns ExternalLinkHandler object with methods and state
 */
export function createExternalLinkHandler(): ExternalLinkHandler {
	let showExternalWarning = false;
	let externalUrl = '';

	function handleExternalLinkClick(e: Event, url: string) {
		e.preventDefault();
		if (e.stopPropagation) {
			e.stopPropagation();
		}
		externalUrl = url;
		showExternalWarning = true;
	}

	function setShowExternalWarning(show: boolean) {
		showExternalWarning = show;
	}

	function setExternalUrl(url: string) {
		externalUrl = url;
	}

	return {
		handleExternalLinkClick,
		showExternalWarning,
		externalUrl,
		setShowExternalWarning,
		setExternalUrl
	};
}

/**
 * Simple handler for components that just need the click handler
 * @param setExternalUrl Function to set the external URL
 * @param setShowWarning Function to show the warning modal
 * @returns Click handler function
 */
export function createSimpleExternalLinkHandler(
	setExternalUrl: (url: string) => void,
	setShowWarning: (show: boolean) => void
) {
	return function handleExternalLinkClick(e: Event, url: string) {
		e.preventDefault();
		if (e.stopPropagation) {
			e.stopPropagation();
		}
		setExternalUrl(url);
		setShowWarning(true);
	};
}

/**
 * Checks if a URL is external (starts with http/https)
 * @param url URL to check
 * @returns true if external, false if internal
 */
export function isExternalUrl(url: string): boolean {
	return url.startsWith('http://') || url.startsWith('https://');
}

/**
 * Handles both external and internal links appropriately
 * @param url URL to navigate to
 * @param handleExternal Function to handle external links
 * @param handleInternal Function to handle internal links (optional)
 */
export function handleLinkClick(
	url: string,
	handleExternal: (url: string) => void,
	handleInternal?: (url: string) => void
) {
	if (isExternalUrl(url)) {
		handleExternal(url);
	} else if (handleInternal) {
		handleInternal(url);
	} else {
		// Default internal link behavior
		window.location.href = url;
	}
}