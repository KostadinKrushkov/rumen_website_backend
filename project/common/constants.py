class ResponseConstants:
    # BLOGS
    POST_BLOG_SUCCESS = "Successfully added new blog."
    POST_BLOG_FAIL_DUPLICATE = "Failed to insert blog due to duplicate title."
    POST_BLOG_FAIL = "Internal error, could not create blog."

    UPDATE_BLOG_SUCCESS = "Blog updated successfully."
    UPDATE_BLOG_NOT_FOUND = "No blog with such title exists."
    UPDATE_BLOG_FAIL = "Internal error, could not update blog."

    GET_ALL_BLOGS_SUCCESS = "Successfully retrieved all blogs."
    GET_ALL_BLOGS_FAIL = "Internal error, could not get all blogs."
    GET_BLOG_BY_TITLE_SUCCESS = "Successfully retrieved blog."
    GET_BLOG_WRONG_PARAMETER = "Error, client must supply valid title as parameter."
    GET_BLOG_BY_TITLE_NOT_FOUND = "Could not get blog, no blog with such title exists."
    GET_BLOG_BY_TITLE_FAIL = "Internal error, could not get blog by title."

    DELETE_BLOG_SUCCESS = "Blog deleted successfully."
    DELETE_BLOG_FAIL_NOT_FOUND = "Could not delete blog, no blog with such title exists."
    DELETE_BLOG_WRONG_PARAMETER = GET_BLOG_WRONG_PARAMETER
    DELETE_BLOG_FAIL = "Internal error, could not delete blog."

    # PICTURES
    POST_PICTURE_SUCCESS = "Successfully added new picture."
    POST_PICTURE_FAIL_DUPLICATE_OR_OTHER = "Failed to insert picture due to duplicate title."
    POST_PICTURE_FAIL = "Internal error, could not save new picture."

    UPDATE_PICTURE_SUCCESS = "Picture updated successfully."
    UPDATE_PICTURE_FAIL = "Internal error, could not update picture."
    UPDATE_PICTURE_NOT_FOUND = "No picture with such title exists."

    GET_ALL_PICTURES_FAIL = "Internal error, could not get all pictures."
    GET_ALL_PICTURES_SUCCESS = "Successfully retrieved all pictures."
    GET_ALL_PICTURES_SUCCESS = "Successfully retrieved pictures for home."
    GET_PICTURE_BY_TITLE_SUCCESS = "Successfully retrieved picture."
    GET_PICTURE_WRONG_PARAMETER = "Error, client must supply valid title as parameter."
    GET_PICTURE_BY_TITLE_NOT_FOUND = "Could not get picture, no picture with such title exists."
    GET_PICTURE_BY_TITLE_FAIL = "Internal error, could not get picture by title."
    GET_PICTURE_FOR_HOME = "Internal error, could not get pictures for home screen."

    DELETE_PICTURE_SUCCESS = "Picture deleted successfully."
    DELETE_PICTURE_FAIL = "Internal error, could not delete picture."
    DELETE_PICTURE_FAIL_NOT_FOUND = "Could not delete picture, no picture with such title exists."
    DELETE_PICTURE_WRONG_PARAMETER = "Error, client must supply valid title as parameter."

    # CATEGORIES
    POST_CATEGORY_SUCCESS = "Successfully added new category."
    POST_CATEGORY_FAIL_DUPLICATE_OR_OTHER = "Failed to insert category due to duplicate title."
    POST_CATEGORY_FAIL = "Internal error, could not save new category."

    UPDATE_CATEGORY_SUCCESS = "Category updated successfully."
    UPDATE_CATEGORY_NOT_FOUND = "No category with such name exists."
    UPDATE_CATEGORY_FAIL = "Internal error, could not update category."

    GET_ALL_CATEGORIES_SUCCESS = "Successfully retrieved all categories."
    GET_ALL_CATEGORIES_FAIL = "Internal error, could not get all categories."
    GET_CATEGORY_BY_NAME_SUCCESS = "Successfully retrieved category."
    GET_CATEGORY_WRONG_PARAMETER = "Error, client must supply valid name as parameter."
    GET_CATEGORY_BY_NAME_NOT_FOUND = "Could not get category, no category with such name exists."
    GET_CATEGORY_BY_NAME_FAIL = "Internal error, could not get category by name."

    DELETE_CATEGORY_SUCCESS = "Category deleted successfully."
    DELETE_CATEGORY_FAIL_NOT_FOUND = "Could not delete category, no category with such title exists."
    DELETE_CATEGORY_WRONG_PARAMETER = "Error, client must supply valid name as parameter."
    DELETE_CATEGORY_FAIL_IS_IN_USE = "Error, client must make sure no picture uses this category before deleting."
    DELETE_CATEGORY_FAIL = "Internal error, could not delete category."

    # USERS
    SUCCESSFULLY_LOGGED_IN = "Successfully logged in."
    SUCCESSFULLY_LOGGED_IN_AS_ADMIN = "Successfully logged in as admin."
    SUCCESSFULLY_LOGGED_OUT = "Successfully logged out."
    SUCCESSFULLY_REGISTERED = "Successfully registered."
    INCORRECT_CREDENTIALS_FOR_LOGIN = "Error, email or password are wrong. Please check your details."
    INCORRECT_CREDENTIALS_FOR_REGISTER = "Incorrect user data, please make sure the email, password and username are valid."
    ERROR_USER_ALREADY_EXISTS = "Error, user with such email has already been created."
    ERROR_USER_IS_NOT_ACTIVE = "Error, this user is not active. Please verify your account via the email you provided."
    ERROR_USER_IS_NOT_AUTHORIZED = "Error, this user is not authorized."
    ERROR_USER_IS_NOT_AUTHENTICATED = "Error, this user is not authenticated."
    GENERIC_SERVER_ERROR = "Some internal error occurred. Please try again."

    # SMTP
    SUCCESSFULLY_SENT_EMAIL = "Message sent successfully."
    ERROR_FAILED_TO_SEND_EMAIL = "Some internal error occurred and your message was not sent. Please try again."
    DAILY_LIMIT_EXCEEDED = "Daily limit for message reached. Please try again tomorrow."

    # TOKEN
    MISSING_TOKEN = "Error, authentication token was not provided."
    INVALID_TOKEN = "Error, authentication token is not valid."
    EXPIRED_TOKEN = "Error, authentication token has expired, please log in again."

    # GENERIC
    SUCCESS = 'success'
    FAILURE = 'fail'

    # RECAPTCHA
    INVALID_RECAPTCHA_ERROR = "ERROR, reCAPTCHA is not valid, please try again."


class StatusCodes:
    SUCCESS = 200
    SUCCESSFULLY_CREATED = 201

    BAD_REQUEST = 400
    UNAUTHENTICATED = 401
    UNAUTHORIZED = 403
    NOT_FOUND = 404
    INVALID_TOKEN = 498
    INTERNAL_SERVER_ERROR = 500


class SQLConstants:
    DUPLICATE_KEY_ERROR = "duplicate key"
