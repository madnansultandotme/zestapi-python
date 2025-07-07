# ZestAPI Security Policy

## Supported Versions

We actively support the following versions of ZestAPI with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

The ZestAPI team takes security bugs seriously. We appreciate your efforts to responsibly disclose your findings, and will make every effort to acknowledge your contributions.

### Where to Report

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report security vulnerabilities to:

- **Email**: info.adnansultan@gmail.com
- **Subject**: [SECURITY] ZestAPI Security Issue
- **GPG Key**: [Optional - Contact for GPG key if needed]

### What to Include

Please include the following information in your report:

1. **Description** of the vulnerability
2. **Steps to reproduce** the issue
3. **Potential impact** of the vulnerability
4. **Suggested fix** (if you have one)
5. **Your contact information** for follow-up

### Response Timeline

We aim to respond to security reports within **48 hours** and will keep you updated on our progress.

Our process:
1. **Acknowledge** receipt of your report (within 48 hours)
2. **Investigate** and validate the issue (within 1 week)
3. **Develop** and test a fix (timeline varies by complexity)
4. **Release** a security update
5. **Publicly disclose** the vulnerability (after fix is available)

### Security Best Practices

When using ZestAPI in production, we recommend:

1. **Keep ZestAPI updated** to the latest version
2. **Use strong JWT secrets** (256-bit or longer)
3. **Enable HTTPS** in production
4. **Configure CORS** properly for your domain
5. **Use environment variables** for sensitive configuration
6. **Enable rate limiting** to prevent abuse
7. **Monitor logs** for suspicious activity
8. **Follow the production deployment guide**

### Security Features

ZestAPI includes several built-in security features:

- **JWT Authentication** with configurable expiration
- **Rate Limiting** with customizable rules
- **CORS Protection** with domain whitelisting
- **Input Validation** with Pydantic models
- **Error Handling** that doesn't leak sensitive information
- **Secure Headers** middleware available
- **Production Configuration** templates

### Hall of Fame

We recognize security researchers who help make ZestAPI more secure:

- *Your name could be here!*

### Questions?

If you have questions about this security policy, please contact:

- **Email**: info.adnansultan@gmail.com
- **GitHub Discussions**: [ZestAPI Discussions](https://github.com/madnansultandotme/zestapi-python/discussions)

---

Thank you for helping keep ZestAPI and its users safe! 🔒
