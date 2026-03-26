# Create a web application
builder.create_web_app(
    name="E-Commerce Platform",
    frontend="react",
    backend="nodejs",
    database="mongodb"
)

# Create API service
builder.create_api_service(
    name="User Management API",
    framework="fastapi",
    authentication="jwt",
    database="postgresql"
)

# Create data science project
builder.create_data_science_project(
    name="Sales Predictor",
    ml_framework="tensorflow",
    analysis_tools="pandas,seaborn"
)