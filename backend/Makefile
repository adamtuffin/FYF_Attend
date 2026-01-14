# Find Your Feet CIC - SAM Build Makefile
# This Makefile is used by SAM CLI to build the Lambda deployment package

.PHONY: build-FYFAttendanceFunction

build-FYFAttendanceFunction:
	# Install Python dependencies
	pip install -r requirements.txt -t $(ARTIFACTS_DIR)/
	
	# Copy application code
	cp -r app.py $(ARTIFACTS_DIR)/
	cp -r lambda_handler.py $(ARTIFACTS_DIR)/
	cp -r src $(ARTIFACTS_DIR)/
	
	# Copy frontend templates (for server-side rendering)
	mkdir -p $(ARTIFACTS_DIR)/templates
	cp -r ../frontend/templates/* $(ARTIFACTS_DIR)/templates/
	
	# Note: Static assets are served from S3/CloudFront, not Lambda
	# Only copy essential static files needed for error pages
	mkdir -p $(ARTIFACTS_DIR)/static/images
	cp ../frontend/static/images/LOGO.webp $(ARTIFACTS_DIR)/static/images/ || true
