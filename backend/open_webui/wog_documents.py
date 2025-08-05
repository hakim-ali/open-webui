"""
Whole of Government (WOG) Documents Module
Organizes government documents by department with enhanced metadata
"""

from typing import Dict, List, Any


def get_wog_documents_by_department() -> List[Dict[str, Any]]:
    """Get WOG documents organized by department with enhanced structure"""
    
    documents = [
        {
            "name": "Finance Department",
            "nameAr": "إدارة المالية",
            "documents": [
                {
                    "title": "Abu Dhabi Government Finance Policy Manual AR",
                    "summaryEn": "Manual outlining finance policies and procedures for Abu Dhabi government entities.",
                    "summaryAr": "دليل شامل يوضح السياسات والإجراءات المالية لكيانات حكومة أبوظبي."
                },
                {
                    "title": "Abu Dhabi Government Finance Policy Manual EN",
                    "summaryEn": "Official English version of Abu Dhabi's finance policy manual for government entities.",
                    "summaryAr": "النسخة الإنجليزية الرسمية لدليل السياسات المالية لحكومة أبوظبي."
                }
            ]
        },
        {
            "name": "Human Resources Department",
            "nameAr": "إدارة الموارد البشرية",
            "documents": [
                {
                    "title": "Circular No. 1 of 2021 regarding the secondment allowance AR",
                    "summaryEn": "Circular on rules for disbursing secondment allowances to government employees.",
                    "summaryAr": "تعميم حول قواعد صرف بدل الإعارة لموظفي الحكومة."
                },
                {
                    "title": "Circular No. 3 of 2022 regulating promotion schedules and performance management AR",
                    "summaryEn": "Circular regulating promotion cycles and performance management in government.",
                    "summaryAr": "تعميم ينظم جداول الترقيات وإدارة الأداء في الحكومة."
                },
                {
                    "title": "Circular No. 4 of 2021 the unified performance management system for government entities AR",
                    "summaryEn": "Circular introducing a unified performance management system for government entities.",
                    "summaryAr": "تعميم يقدم نظام إدارة الأداء الموحد للجهات الحكومية."
                },
                {
                    "title": "Circular No. 7 of 2020 determining the percentage of people with disabilities in government entities AR",
                    "summaryEn": "Circular on required percentage of people with disabilities in government entities.",
                    "summaryAr": "تعميم يحدد نسبة توظيف أصحاب الهمم في الجهات الحكومية."
                },
                {
                    "title": "Circular No. 8 of 2021 regarding instructions for disbursing the secondment allowance AR",
                    "summaryEn": "Updated instructions for secondment allowance disbursement for government employees.",
                    "summaryAr": "تعليمات محدثة لصرف بدل الإعارة لموظفي الحكومة."
                },
                {
                    "title": "Government Employee Guide Version 1 AR",
                    "summaryEn": "First version of employee guide outlining rights, duties, and HR processes.",
                    "summaryAr": "النسخة الأولى من دليل الموظف توضح الحقوق والواجبات وإجراءات الموارد البشرية."
                },
                {
                    "title": "Government Employee Guide Version 2 AR",
                    "summaryEn": "Second version of employee guide focusing on ethics and conduct in government.",
                    "summaryAr": "النسخة الثانية من دليل الموظف تركز على الأخلاقيات والسلوكيات."
                },
                {
                    "title": "HR Law EN",
                    "summaryEn": "English version of HR law covering government employment rights and duties.",
                    "summaryAr": "النسخة الإنجليزية من قانون الموارد البشرية يشمل الحقوق والواجبات للموظفين الحكوميين."
                },
                {
                    "title": "HR Law AR",
                    "summaryEn": "HR law for government employees, specifying rights, obligations, and regulations.",
                    "summaryAr": "قانون الموارد البشرية لموظفي الحكومة يحدد الحقوق والواجبات واللوائح."
                },
                {
                    "title": "Implementation Regulation for HR Law No 6 Year 2016 AR",
                    "summaryEn": "Guidelines for implementing HR Law No. 6 of 2016 for government entities.",
                    "summaryAr": "إرشادات تنفيذية لقانون الموارد البشرية رقم 6 لعام 2016 للجهات الحكومية."
                },
                {
                    "title": "Implementation Regulation for HR Law No 6 Year 2016 EN",
                    "summaryEn": "English translation of implementing regulations for HR Law No. 6 of 2016.",
                    "summaryAr": "الترجمة الإنجليزية للائحة التنفيذية لقانون الموارد البشرية رقم 6 لعام 2016."
                }
            ]
        },
        {
            "name": "Procurement Department",
            "nameAr": "إدارة المشتريات",
            "documents": [
                {
                    "title": "DGE Procurement Framework EN",
                    "summaryEn": "Procurement framework for DGE covering policies and management procedures.",
                    "summaryAr": "إطار المشتريات الخاص بـ DGE يشمل السياسات وإجراءات الإدارة."
                },
                {
                    "title": "Policies and Procedures for Sales Auctions and Warehouses AR",
                    "summaryEn": "Procedures for managing sales auctions and warehouses in Abu Dhabi.",
                    "summaryAr": "إجراءات إدارة مزادات البيع والمستودعات في أبوظبي."
                },
                {
                    "title": "Policies and Procedures for Sales Auctions and Warehouses EN",
                    "summaryEn": "Policies and processes for sales auctions and warehouse management.",
                    "summaryAr": "السياسات والعمليات الخاصة بمزادات البيع وإدارة المستودعات."
                },
                {
                    "title": "Procurement Charter AR",
                    "summaryEn": "Procurement charter outlining governance and roles in Arabic.",
                    "summaryAr": "ميثاق المشتريات يحدد الحوكمة والأدوار."
                },
                {
                    "title": "Procurement Charter EN",
                    "summaryEn": "English version of procurement charter detailing governance and committees.",
                    "summaryAr": "النسخة الإنجليزية من ميثاق المشتريات توضح الحوكمة واللجان."
                },
                {
                    "title": "Procurement Manual (Ariba Aligned) EN",
                    "summaryEn": "Operational manual aligned with SAP Ariba for procurement activities.",
                    "summaryAr": "دليل تشغيلي متوافق مع SAP Ariba لأنشطة المشتريات."
                },
                {
                    "title": "Procurement Manual (Business Process) AR",
                    "summaryEn": "Arabic manual on procurement processes and strategies for government.",
                    "summaryAr": "دليل عربي حول عمليات واستراتيجيات المشتريات الحكومية."
                },
                {
                    "title": "Procurement Manual (Business Process) EN",
                    "summaryEn": "Guide to procurement business processes and documentation standards.",
                    "summaryAr": "دليل العمليات التجارية للمشتريات ومعايير التوثيق."
                },
                {
                    "title": "Procurement Standard Regulations AR",
                    "summaryEn": "Official procurement standards and regulations for Abu Dhabi.",
                    "summaryAr": "المعايير واللوائح الرسمية للمشتريات في أبوظبي."
                },
                {
                    "title": "Procurement Standard Regulations EN",
                    "summaryEn": "English document of procurement standards and operational procedures.",
                    "summaryAr": "وثيقة المعايير والإجراءات التشغيلية للمشتريات باللغة الإنجليزية."
                },
                {
                    "title": "Support Frequently Asked Questions EN",
                    "summaryEn": "FAQ document covering procurement framework and compliance queries.",
                    "summaryAr": "وثيقة الأسئلة الشائعة حول إطار المشتريات والاستفسارات المتعلقة بالامتثال."
                }
            ]
        },
        {
            "name": "Customer Experience Department",
            "nameAr": "إدارة تجربة العميل",
            "documents": [
                {
                    "title": "Abu Dhabi Government Tone of Voice Document",
                    "summaryEn": "A guide outlining the tone, language style, and communication principles for Abu Dhabi Government entities, ensuring consistent, clear, and engaging communication with customers.",
                    "summaryAr": "دليل يوضح أسلوب اللغة ومبادئ التواصل للجهات الحكومية في أبوظبي، لضمان تواصل متسق وواضح وجذاب مع العملاء."
                },
                {
                    "title": "Effortless Guide AR",
                    "summaryEn": "Official Abu Dhabi government policy in Arabic, detailing the strategy and requirements for providing an effortless customer experience across all government entities and channels.",
                    "summaryAr": "سياسة رسمية لحكومة أبوظبي باللغة العربية توضح الاستراتيجية والمتطلبات لتقديم تجربة عميل سلسة عبر جميع الجهات والقنوات الحكومية."
                },
                {
                    "title": "Effortless Guide EN V2",
                    "summaryEn": "Comprehensive English guide for Abu Dhabi's Effortless Customer Experience Program, describing the framework, best practices, and operational guidelines for improving government services and customer satisfaction.",
                    "summaryAr": "دليل شامل باللغة الإنجليزية لبرنامج تجربة العميل السلسة في أبوظبي، يوضح الإطار والممارسات المثلى والإرشادات التشغيلية لتحسين الخدمات الحكومية ورضا المتعاملين."
                },
                {
                    "title": "Glossary",
                    "summaryEn": "A glossary of key customer experience (CX) terms in both English and Arabic, serving as a reference for terminology used in Abu Dhabi's government service initiatives.",
                    "summaryAr": "مسرد لمصطلحات تجربة العميل (CX) الأساسية باللغتين الإنجليزية والعربية، يُستخدم كمرجع للمصطلحات ضمن مبادرات خدمات حكومة أبوظبي."
                },
                {
                    "title": "TOV templates",
                    "summaryEn": "A set of communication templates and examples (in English and Arabic) for Abu Dhabi government staff, covering SMS, email, and notification messages to ensure a consistent and user‑friendly tone of voice.",
                    "summaryAr": "مجموعة من قوالب وأمثلة التواصل (بالإنجليزية والعربية) لموظفي حكومة أبوظبي، تغطي الرسائل النصية والبريد الإلكتروني والإشعارات لضمان أسلوب موحّد وسهل في التواصل."
                }
            ]
        }
    ]
    
    return documents 