"""
Mobile configuration for GovGPT
This module provides mobile-specific configuration including locales, suggestions, and app settings.
"""

from typing import Dict, List, Any
from fastapi.responses import JSONResponse
from open_webui.locales import get_english_locale, get_arabic_locale


def get_mobile_suggestions(app_state) -> List[Dict[str, Any]]:
    """Get enhanced suggestions with Arabic support and better structure."""
    # Try to get suggestions from app state config first
    config = app_state.config
    default_suggestions = getattr(config, 'DEFAULT_PROMPT_SUGGESTIONS', [])
    
    if default_suggestions:
        # Use the suggestions from app state config
        return default_suggestions
    else:
        # Fallback to default suggestions if none are configured
        return [
            {
                "id": "find_document",
                "title": "Find document",
                "title_ar": "البحث عن مستند",
                "content": "Help me find the official document, policy, or guideline related to ",
                "content_ar": "ساعدني في العثور على المستند الرسمي أو السياسة أو الإرشادات المتعلقة بـ",
                "icon_name": "find_document",
                "icon_color": "#F57851",
                "category": "search",
                "keywords": ["document", "policy", "guide", "بحث"]
            },
            {
                "id": "summarize_text",
                "title": "Summarize text",
                "title_ar": "تلخيص النص",
                "content": "Please summarize the following text and highlight the key points or conclusions ",
                "content_ar": "يرجى تلخيص النص التالي وتسليط الضوء على النقاط أو الاستنتاجات الرئيسية",
                "icon_name": "summarize_text",
                "icon_color": "#CC7A00",
                "category": "analysis",
                "keywords": ["summary", "text", "key points", "تلخيص"]
            },
            {
                "id": "draft_message",
                "title": "Draft message",
                "title_ar": "صياغة رسالة",
                "content": "Help me draft a message, such as an email or memo regarding the following ",
                "content_ar": "ساعدني في صياغة رسالة، مثل بريد إلكتروني أو مذكرة بخصوص التالي",
                "icon_name": "draft_message",
                "icon_color": "#007AFF",
                "category": "writing",
                "keywords": ["draft", "message", "compose", "رسالة"]
            },
            {
                "id": "compare_content",
                "title": "Compare content",
                "title_ar": "مقارنة المحتوى",
                "content": "Compare the following documents/text and highlight the key differences or similarities ",
                "content_ar": "قارن بين المستندات/النصوص التالية وسلط الضوء على الفروقات أو التشابهات",
                "icon_name": "compare_content",
                "icon_color": "#008A57",
                "category": "analysis",
                "keywords": ["compare", "difference", "similarity", "مقارنة"]
            },
            {
                "id": "explain_simply",
                "title": "Explain simply",
                "title_ar": "شرح مبسط",
                "content": "Explain the following in a simple and easy-to-understand way ",
                "content_ar": "اشرح التالي بطريقة بسيطة وسهلة الفهم",
                "icon_name": "explain_simply",
                "icon_color": "#6C63FF",
                "category": "education",
                "keywords": ["explain", "simple", "clarify", "شرح"]
            },
            {
                "id": "make_a_plan",
                "title": "Make a plan",
                "title_ar": "إنشاء خطة",
                "content": "Help me create a step-by-step plan to accomplish the following ",
                "content_ar": "ساعدني في إنشاء خطة خطوة بخطوة لإنجاز التالي",
                "icon_name": "make_a_plan",
                "icon_color": "#FFB300",
                "category": "planning",
                "keywords": ["plan", "steps", "strategy", "خطة"]
            },
            {
                "id": "analyze_data",
                "title": "Analyze data",
                "title_ar": "تحليل البيانات",
                "content": "Help me analyze the following dataset and identify key patterns and insights ",
                "content_ar": "ساعدني في تحليل مجموعة البيانات التالية وتحديد الأنماط والرؤى الرئيسية",
                "icon_name": "analyze_data",
                "icon_color": "#009688",
                "category": "analysis",
                "keywords": ["analyze", "data", "insights", "تحليل"]
            },
            {
                "id": "brainstorm_ideas",
                "title": "Brainstorm ideas",
                "title_ar": "عصف ذهني للأفكار",
                "content": "Let's brainstorm creative ideas for the following ",
                "content_ar": "دعنا نبتكر أفكارًا إبداعية حول التالي",
                "icon_name": "brainstorm_ideas",
                "icon_color": "#cc7a00",
                "category": "creativity",
                "keywords": ["brainstorm", "ideas", "innovation", "أفكار"]
            }
        ]


def get_feedback_options() -> Dict[str, List[Dict[str, str]]]:
    """Get feedback options for positive and negative feedback."""
    return {
        "positive": [
            {
                "id": "accurate_and_correct",
                "title_en": "Accurate/Correct",
                "title_ar": "دقيق/صحيح"
            },
            {
                "id": "clear_and_easy_to_follow",
                "title_en": "Easy to follow",
                "title_ar": "واضح وسهل المتابعة"
            },
            {
                "id": "complete_and_detailed",
                "title_en": "Detailed/Completed",
                "title_ar": "مفصل/مكتمل"
            },
            {
                "id": "relevant_to_my_need",
                "title_en": "Relevant",
                "title_ar": "ذو صلة باحتياجي"
            },
            {
                "id": "well_structured_and_formatted",
                "title_en": "Well structured/Formatted",
                "title_ar": "منظم/منسق بشكل جيد"
            },
            {
                "id": "other",
                "title_en": "Other",
                "title_ar": "أخرى"
            }
        ],
        "negative": [
            {
                "id": "factually_incorrect",
                "title_en": "Factually incorrect",
                "title_ar": "غير صحيح من الناحية الواقعية"
            },
            {
                "id": "incomplete_or_missing_details",
                "title_en": "Incomplete/Missing details",
                "title_ar": "غير مكتمل أو يفتقر إلى التفاصيل"
            },
            {
                "id": "off_topic_or_irrelevant",
                "title_en": "Off-topic/Irrelevant",
                "title_ar": "خارج الموضوع/غير ذي صلة"
            },
            {
                "id": "too_technical_or_jargon_heavy",
                "title_en": "Too technical/Jargon-heavy",
                "title_ar": "تقني للغاية/مليء بالمصطلحات"
            },
            {
                "id": "poor_structure_or_formatting",
                "title_en": "Poor structure/Formatting",
                "title_ar": "هيكل ضعيف/تنسيق غير جيد"
            },
            {
                "id": "other",
                "title_en": "Other",
                "title_ar": "أخرى"
            }
        ]
    }


def get_mobile_config(app_state) -> Dict[str, Any]:
    """Generate mobile configuration using app state values."""
    
    # Read values from app.state.config
    config = app_state.config
    
    return {
        "suggestions": get_mobile_suggestions(app_state),
        "fileUploadCountAllowed": getattr(config, 'FILE_MAX_COUNT', 5),
        "maxFileSizeAllowed": getattr(config, 'FILE_MAX_SIZE', 10485760),
        "fileTypesAllowed": getattr(config, 'ALLOWED_FILE_EXTENSIONS', ["pdf"]),
        "privacyPolicyURL": "/privacy",
        "termsConditionsURL": "/terms",
        "govgpt": {
            "rag_wog_model_name": getattr(config, 'GOVGPT_RAG_WOG_MODEL_NAME', 'govgpt_rag_wog'),
        },
        "default_models": getattr(config, 'DEFAULT_MODELS', None),
        "allowCredentialsLogin": True,
        "allowWebSearch": getattr(config, 'ENABLE_WEB_SEARCH', False),
        "allowRagSearch": getattr(config, 'ENABLE_RAG_HYBRID_SEARCH', False),
        "inputLinesNum": 8,
        "editLinesNum": 20,
        "maintenance": {
            "enabled": False,
            "scheduled": {
                "start": "2025-10-01T00:00:00Z",
                "end": "2025-10-01T02:00:00Z"
            }
        },
        "appVersions": {
            "ios": {
                "currentProd": "2.0.0",
                "forceUpdateProd": "2.0.0"
            },
            "android": {
                "currentProd": "2.0.0",
                "forceUpdateProd": "2.0.0"
            }
        },
        "feedback": get_feedback_options(),
        "locales": {
            "default": "en",
            "en": get_english_locale(),
            "ar": get_arabic_locale()
        }
    } 