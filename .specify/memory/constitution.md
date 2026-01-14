<!--
  ===========================================================================
  SYNC IMPACT REPORT
  ===========================================================================
  Version Change: 1.2.0 → 1.2.1
  
  Modified Principles:
    - V. Data Protection & Privacy: Added secrets management requirements
  
  Modified Sections: None
  
  Added Sections: None
  
  Removed Sections: None
  
  Templates Requiring Updates:
    ✅ plan-template.md - No updates needed (secrets covered under Data Protection)
    ✅ spec-template.md - No updates needed
    ✅ tasks-template.md - No updates needed
    ✅ agent-file-template.md - No updates needed
    ✅ checklist-template.md - No updates needed
  
  Follow-up TODOs: None
  ===========================================================================
-->

# Find Your Feet CIC Constitution

## Core Principles

### I. Accessibility First

All applications MUST meet WCAG 2.1 Level AA compliance as a minimum standard. This is non-negotiable for a charity serving diverse communities.

- Every interactive element MUST be keyboard accessible
- All images MUST have meaningful alt text
- Colour contrast MUST meet minimum ratios (4.5:1 for normal text, 3:1 for large text)
- Forms MUST have properly associated labels and clear error messages
- Focus states MUST be visible and clear
- Screen reader compatibility MUST be tested before deployment

**Rationale**: Find Your Feet CIC serves people from all backgrounds and abilities. Excluding anyone through inaccessible design contradicts our charitable mission.

### II. Plain Language

All user-facing content MUST be written in plain, easy-to-understand English. Avoid jargon, technical terms, and complex sentence structures.

- Reading level SHOULD target age 9-11 (approximately Year 5-6 reading level)
- Instructions MUST use simple, direct language
- Error messages MUST explain what went wrong and how to fix it in everyday words
- Technical concepts MUST be explained without assuming prior knowledge
- Button labels and navigation MUST use common, recognisable terms

**Rationale**: Our services reach people with varying literacy levels and those for whom English may not be their first language. Clear communication ensures nobody is left behind.

### III. Serverless & Well-Architected

All backend services MUST follow AWS serverless patterns and comply with the AWS Well-Architected Framework to ensure cost-effectiveness, scalability, security, and operational excellence.

#### Serverless Requirements

- Functions MUST be implemented as AWS Lambda with Python runtime
- APIs MUST use Amazon API Gateway
- Data storage MUST use appropriate serverless services (DynamoDB, S3, Aurora Serverless)
- Asynchronous processing MUST use SQS, SNS, or EventBridge
- Each microservice MUST be independently deployable
- Infrastructure MUST be defined as code using AWS CloudFormation

#### Local Development Requirements

All code MUST be runnable locally without requiring AWS credentials or live AWS services. A configuration switch MUST enable substitution of AWS components with local equivalents.

- A `LOCAL_MODE` or equivalent environment variable MUST toggle between local and AWS execution
- DynamoDB MUST be substitutable with DynamoDB Local or an in-memory equivalent
- S3 MUST be substitutable with local file storage or MinIO
- Lambda functions MUST be invokable directly as Python functions for local testing
- API Gateway endpoints MUST be testable via a local HTTP server (e.g., Flask, FastAPI)
- SQS/SNS MUST be substitutable with in-memory queues or LocalStack equivalents
- All local substitutes MUST maintain the same interface contracts as AWS services

**Rationale**: Developers must be able to run, test, and debug code without AWS costs or connectivity. Local development accelerates feedback loops and reduces cloud spend during development.

#### AWS Well-Architected Framework Compliance

All deployments MUST be reviewed against the six pillars of the AWS Well-Architected Framework:

1. **Operational Excellence**: Automated deployments, runbooks for incidents, monitoring dashboards
2. **Security**: Least privilege IAM, encryption, security group reviews, secrets management via Secrets Manager
3. **Reliability**: Multi-AZ where appropriate, graceful degradation, retry logic with exponential backoff
4. **Performance Efficiency**: Right-sized Lambda memory, caching strategies, async patterns for long operations
5. **Cost Optimisation**: Reserved capacity where predictable, lifecycle policies, resource tagging for cost allocation
6. **Sustainability**: Efficient code paths, appropriate data retention, serverless-first to reduce idle resources

**Rationale**: As a charity, operational costs and maintenance overhead must be minimised. The Well-Architected Framework ensures our infrastructure is secure, resilient, and cost-effective while serverless architecture scales with usage and eliminates server management.

### IV. Brand Consistency

All applications MUST adhere to Find Your Feet CIC visual identity guidelines to maintain a professional, recognisable presence.

- Primary colour: `#F36F21` (Orange) - Used for primary actions, key highlights, and brand elements
- Secondary colour: `#D8D9D1` (Light Grey) - Used for backgrounds and subtle UI elements
- Tertiary colour: `#333333` (Dark Grey) - Used for text and high-contrast elements
- Logo: Use `LOGO.webp` consistently; never distort or recolour
- Tailwind CSS MUST be configured with brand colours as custom theme values
- Headings MUST use **Futura** font family
- Body text MUST use **Avenir** font family
- Typography MUST be legible, friendly, and appropriate for the charitable sector

**Rationale**: Consistent branding builds trust and recognition. Users should immediately know they are interacting with a Find Your Feet CIC service.

### V. Data Protection & Privacy

All applications MUST comply with UK GDPR and the Data Protection Act 2018. Protecting participant and volunteer data is paramount.

#### Data Handling

- Personal data MUST only be collected when necessary
- Data retention policies MUST be clearly defined and enforced
- Users MUST be informed about what data is collected and why
- Consent MUST be explicit and recorded
- Data MUST be encrypted at rest and in transit
- Access to personal data MUST be role-based and auditable
- Data Subject Access Requests MUST be supportable within legal timeframes

#### Secrets Management

Secrets, credentials, and sensitive configuration MUST NEVER be stored directly in code or committed to version control.

- API keys, passwords, and tokens MUST be stored in AWS Secrets Manager or environment variables
- `.env` files containing secrets MUST be listed in `.gitignore`
- Secrets MUST be injected at runtime, never hardcoded
- Local development MUST use `.env.local` or equivalent for local-only secrets
- Code reviews MUST verify no secrets are present in commits
- Pre-commit hooks SHOULD scan for accidental secret inclusion

**Rationale**: As a Community Interest Company handling personal data, we have legal and ethical obligations to protect the people we serve. Leaked credentials can compromise entire systems and user data.

### VI. Test-Driven Quality

All features MUST be developed with appropriate testing to ensure reliability and prevent regressions.

- Unit tests MUST cover business logic
- Integration tests MUST verify API contracts
- Accessibility tests MUST be included in the test suite (e.g., axe-core, pa11y)
- Frontend components MUST be tested for correct rendering
- Tests MUST run in CI/CD pipeline before deployment
- Critical user journeys MUST have end-to-end tests

**Rationale**: Our users depend on these systems. Bugs and outages directly impact the charity's ability to deliver its mission.

## Technology Stack & Architecture

### Backend

- **Runtime**: Python 3.11+
- **Framework**: AWS Lambda with API Gateway
- **Database**: DynamoDB (primary), S3 (file storage)
- **Infrastructure**: AWS CloudFormation
- **Testing**: pytest with moto for AWS mocking
- **Local Development**: DynamoDB Local, local file storage, Flask/FastAPI for API testing

### Frontend

- **Styling**: Tailwind CSS with custom brand configuration
- **Templating**: Jinja2 or appropriate Python-compatible solution
- **Bundling**: Minimised CSS and assets for performance
- **Accessibility**: Semantic HTML, ARIA attributes where needed

### DevOps

- **CI/CD**: GitHub Actions or AWS CodePipeline
- **Monitoring**: CloudWatch with appropriate alarms
- **Logging**: Structured JSON logging to CloudWatch Logs
- **Environments**: Development (Staging and Production to be added as needed)

## Visual Identity & Brand Guidelines

### Colour Palette

| Name       | Hex       | RGB              | Usage                                          |
|------------|-----------|------------------|------------------------------------------------|
| Primary    | `#F36F21` | `rgb(243,111,33)`| Primary buttons, links, key highlights, icons  |
| Secondary  | `#D8D9D1` | `rgb(216,217,209)`| Cards, subtle UI elements                     |
| Tertiary   | `#333333` | `rgb(51,51,51)`  | Body text, headings, high-contrast elements    |
| Background | `#242323` | `rgb(36,35,35)`  | Page background, dark theme base               |

### Typography

| Element | Font Family | Usage |
|---------|-------------|-------|
| Headings | **Futura** | h1-h6, navigation, buttons, prominent labels |
| Body | **Avenir** | Paragraphs, form fields, descriptions, general content |

Font fallbacks SHOULD include system fonts for performance:
- Futura: `'Futura', 'Trebuchet MS', sans-serif`
- Avenir: `'Avenir', 'Avenir Next', 'Segoe UI', sans-serif`

### Tailwind Configuration

All projects MUST extend Tailwind with the following theme:

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        'fyf-primary': '#F36F21',
        'fyf-secondary': '#D8D9D1',
        'fyf-tertiary': '#333333',
        'fyf-background': '#242323',
      },
      fontFamily: {
        'heading': ['Futura', 'Trebuchet MS', 'sans-serif'],
        'body': ['Avenir', 'Avenir Next', 'Segoe UI', 'sans-serif'],
      }
    }
  }
}
```

### Logo Usage

- Logo file: `LOGO.webp`
- MUST maintain original aspect ratio
- MUST have sufficient contrast against backgrounds
- Minimum clear space equal to logo height on all sides

## Governance

This constitution is the authoritative guide for all Find Your Feet CIC digital projects. It supersedes any conflicting practices or ad-hoc decisions.

### Amendment Process

1. Proposed changes MUST be documented with rationale
2. Changes affecting core principles require stakeholder review
3. All amendments MUST update the version number and Last Amended date
4. Migration plans MUST accompany breaking changes

### Versioning Policy

- **MAJOR**: Principle removed, redefined, or backward-incompatible governance change
- **MINOR**: New principle added, section materially expanded
- **PATCH**: Clarifications, typos, non-semantic refinements

### Compliance

- All pull requests MUST reference relevant constitution principles
- Code reviews MUST verify accessibility compliance
- Deployment gates MUST include automated accessibility testing
- Regular audits SHOULD verify ongoing compliance

### Reference Documents

- Use `agent-file-template.md` for runtime development guidance
- Use `plan-template.md` for feature implementation planning
- Use `spec-template.md` for feature specifications
- Use `tasks-template.md` for task breakdown

**Version**: 1.3.0 | **Ratified**: 2026-01-13 | **Last Amended**: 2026-01-14
