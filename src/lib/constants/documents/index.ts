export const DOCUMENT = {
    DOC: {
        TYPE: 'application/msword',
        EXTENSION: '.doc'
    },
    DOCX: {
        TYPE: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        EXTENSION: '.docx'
    },
    PDF: {
        TYPE: 'application/pdf',
        EXTENSION: '.pdf'
    }
}

export const DOCUMENT_KEYS = Object.keys(DOCUMENT);
export const DOCUMENT_TYPES = Object.values(DOCUMENT).map((doc) => doc.TYPE);
