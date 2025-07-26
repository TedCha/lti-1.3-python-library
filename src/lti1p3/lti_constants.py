V1_3 = '1.3.0'

# Required message claims
MESSAGE_TYPE = 'https://purl.imsglobal.org/spec/lti/claim/message_type'
VERSION = 'https://purl.imsglobal.org/spec/lti/claim/version'
DEPLOYMENT_ID = 'https://purl.imsglobal.org/spec/lti/claim/deployment_id'
TARGET_LINK_URI = 'https://purl.imsglobal.org/spec/lti/claim/target_link_uri'
RESOURCE_LINK = 'https://purl.imsglobal.org/spec/lti/claim/resource_link'
ROLES = 'https://purl.imsglobal.org/spec/lti/claim/roles'
FOR_USER = 'https://purl.imsglobal.org/spec/lti/claim/for_user'

# Optional message claims
CONTEXT = 'https://purl.imsglobal.org/spec/lti/claim/context'
CUSTOM = 'https://purl.imsglobal.org/spec/lti/claim/custom'
LAUNCH_PRESENTATION = 'https://purl.imsglobal.org/spec/lti/claim/launch_presentation'
LIS = 'https://purl.imsglobal.org/spec/lti/claim/lis'
LTI1P1 = 'https://purl.imsglobal.org/spec/lti/claim/lti1p1'
ROLE_SCOPE_MENTOR = 'https://purl.imsglobal.org/spec/lti/claim/role_scope_mentor'
TOOL_PLATFORM = 'https://purl.imsglobal.org/spec/lti/claim/tool_platform'

# LTI DL
DL_CONTENT_ITEMS = 'https://purl.imsglobal.org/spec/lti-dl/claim/content_items'
DL_DATA = 'https://purl.imsglobal.org/spec/lti-dl/claim/data'
DL_DEEP_LINK_SETTINGS = 'https://purl.imsglobal.org/spec/lti-dl/claim/deep_linking_settings'
DL_RESOURCE_LINK_TYPE = 'ltiResourceLink'

# LTI NRPS
NRPS_CLAIM_SERVICE = 'https://purl.imsglobal.org/spec/lti-nrps/claim/namesroleservice'
NRPS_SCOPE_MEMBERSHIP_READONLY = 'https://purl.imsglobal.org/spec/lti-nrps/scope/contextmembership.readonly'

# LTI AGS
AGS_CLAIM_ENDPOINT = 'https://purl.imsglobal.org/spec/lti-ags/claim/endpoint'
AGS_SCOPE_LINEITEM = 'https://purl.imsglobal.org/spec/lti-ags/scope/lineitem'
AGS_SCOPE_LINEITEM_READONLY = 'https://purl.imsglobal.org/spec/lti-ags/scope/lineitem.readonly'
AGS_SCOPE_RESULT_READONLY = 'https://purl.imsglobal.org/spec/lti-ags/scope/result.readonly'
AGS_SCOPE_SCORE = 'https://purl.imsglobal.org/spec/lti-ags/scope/score'

# LTI GS
GS_CLAIM_SERVICE = 'https://purl.imsglobal.org/spec/lti-gs/claim/groupsservice'

# User Vocab
SYSTEM_ADMINISTRATOR = 'http://purl.imsglobal.org/vocab/lis/v2/system/person#Administrator'
SYSTEM_NONE = 'http://purl.imsglobal.org/vocab/lis/v2/system/person#None'
SYSTEM_ACCOUNTADMIN = 'http://purl.imsglobal.org/vocab/lis/v2/system/person#AccountAdmin'
SYSTEM_CREATOR = 'http://purl.imsglobal.org/vocab/lis/v2/system/person#Creator'
SYSTEM_SYSADMIN = 'http://purl.imsglobal.org/vocab/lis/v2/system/person#SysAdmin'
SYSTEM_SYSSUPPORT = 'http://purl.imsglobal.org/vocab/lis/v2/system/person#SysSupport'
SYSTEM_USER = 'http://purl.imsglobal.org/vocab/lis/v2/system/person#User'
INSTITUTION_ADMINISTRATOR = 'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Administrator'
INSTITUTION_FACULTY = 'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Faculty'
INSTITUTION_GUEST = 'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Guest'
INSTITUTION_NONE = 'http://purl.imsglobal.org/vocab/lis/v2/institution/person#None'
INSTITUTION_OTHER = 'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Other'
INSTITUTION_STAFF = 'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Staff'
INSTITUTION_STUDENT = 'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Student'
INSTITUTION_ALUMNI = 'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Alumni'
INSTITUTION_INSTRUCTOR = 'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Instructor'
INSTITUTION_LEARNER = 'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Learner'
INSTITUTION_MEMBER = 'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Member'
INSTITUTION_MENTOR = 'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Mentor'
INSTITUTION_OBSERVER = 'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Observer'
INSTITUTION_PROSPECTIVESTUDENT = 'http://purl.imsglobal.org/vocab/lis/v2/institution/person#ProspectiveStudent'
MEMBERSHIP_ADMINISTRATOR = 'http://purl.imsglobal.org/vocab/lis/v2/membership#Administrator'
MEMBERSHIP_CONTENTDEVELOPER = 'http://purl.imsglobal.org/vocab/lis/v2/membership#ContentDeveloper'
MEMBERSHIP_INSTRUCTOR = 'http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor'
MEMBERSHIP_LEARNER = 'http://purl.imsglobal.org/vocab/lis/v2/membership#Learner'
MEMBERSHIP_MENTOR = 'http://purl.imsglobal.org/vocab/lis/v2/membership#Mentor'
MEMBERSHIP_MANAGER = 'http://purl.imsglobal.org/vocab/lis/v2/membership#Manager'
MEMBERSHIP_MEMBER = 'http://purl.imsglobal.org/vocab/lis/v2/membership#Member'
MEMBERSHIP_OFFICER = 'http://purl.imsglobal.org/vocab/lis/v2/membership#Officer'

# Context sub-roles
MEMBERSHIP_EXTERNALINSTRUCTOR = 'http://purl.imsglobal.org/vocab/lis/v2/membership/Instructor#ExternalInstructor'
MEMBERSHIP_GRADER = 'http://purl.imsglobal.org/vocab/lis/v2/membership/Instructor#Grader'
MEMBERSHIP_GUESTINSTRUCTOR = 'http://purl.imsglobal.org/vocab/lis/v2/membership/Instructor#GuestInstructor'
MEMBERSHIP_LECTURER = 'http://purl.imsglobal.org/vocab/lis/v2/membership/Instructor#Lecturer'
MEMBERSHIP_PRIMARYINSTRUCTOR = 'http://purl.imsglobal.org/vocab/lis/v2/membership/Instructor#PrimaryInstructor'
MEMBERSHIP_SECONDARYINSTRUCTOR = 'http://purl.imsglobal.org/vocab/lis/v2/membership/Instructor#SecondaryInstructor'
MEMBERSHIP_TA = 'http://purl.imsglobal.org/vocab/lis/v2/membership/Instructor#TeachingAssistant'
MEMBERSHIP_TAGROUP = 'http://purl.imsglobal.org/vocab/lis/v2/membership/Instructor#TeachingAssistantGroup'
MEMBERSHIP_TAOFFERING = 'http://purl.imsglobal.org/vocab/lis/v2/membership/Instructor#TeachingAssistantOffering'
MEMBERSHIP_TASECTION = 'http://purl.imsglobal.org/vocab/lis/v2/membership/Instructor#TeachingAssistantSection'
MEMBERSHIP_TASECTIONASSOCIATION = 'http://purl.imsglobal.org/vocab/lis/v2/membership/Instructor#TeachingAssistantSectionAssociation'
MEMBERSHIP_TATEMPLATE = 'http://purl.imsglobal.org/vocab/lis/v2/membership/Instructor#TeachingAssistantTemplate'

# Context Vocab
COURSE_TEMPLATE = 'http://purl.imsglobal.org/vocab/lis/v2/course#CourseTemplate'
COURSE_OFFERING = 'http://purl.imsglobal.org/vocab/lis/v2/course#CourseOffering'
COURSE_SECTION = 'http://purl.imsglobal.org/vocab/lis/v2/course#CourseSection'
COURSE_GROUP = 'http://purl.imsglobal.org/vocab/lis/v2/course#Group'

# Message Types
MESSAGE_TYPE_DEEPLINK = 'LtiDeepLinkingRequest'
MESSAGE_TYPE_DEEPLINK_RESPONSE = 'LtiDeepLinkingResponse'
MESSAGE_TYPE_RESOURCE = 'LtiResourceLinkRequest'
MESSAGE_TYPE_SUBMISSIONREVIEW = 'LtiSubmissionReviewRequest'
