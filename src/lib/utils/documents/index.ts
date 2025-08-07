import type { DocumentValidationResult } from "$lib/types";
import { DOCUMENT_TYPES, DOCUMENT_KEYS } from "$lib/constants/documents";

export function validateDocuments(files: File[], i18n: any): DocumentValidationResult {
    const validFiles: File[] = [];
    const invalidFileNames: string[] = [];

    for (const file of files) {
        if (DOCUMENT_TYPES.includes(file.type)) {
            validFiles.push(file);
        } else {
            invalidFileNames.push(file.name);
        }
    }

    if (invalidFileNames.length > 0) {
        const message = i18n.t('file.upload.invalidType', {
            FILE_NAME: invalidFileNames.join(', '),
            ALLOWED_FILES: DOCUMENT_KEYS.join(', ')
        });

        return {
            isValid: false,
            validFiles,
            message
        };
    }

    return {
        isValid: true,
        validFiles
    };
}

