# AppPack Skill for Claude Code

An expert assistant skill that provides comprehensive help with [AppPack](https://apppack.io), a Platform-as-a-Service (PaaS) built on AWS.

## What This Skill Does

This skill automatically activates when you ask Claude Code about AppPack-related tasks. It provides:

- **CLI Command Help**: Guidance on all AppPack CLI commands and their options
- **Workflow Assistance**: Step-by-step instructions for deployments, scaling, and troubleshooting
- **Concept Explanations**: Clear explanations of apps, addons, clusters, pipelines, and other AppPack primitives
- **Live Documentation**: Fetches the latest information from [docs.apppack.io](https://docs.apppack.io/)
- **Best Practices**: Recommendations for configuration, security, and operations

## How It Works

Skills in Claude Code are **automatically invoked** by Claude when relevant to your conversation. You don't need to manually activate them.

The skill will load when you:
- Ask about AppPack concepts (e.g., "What's an AppPack cluster?")
- Need help with CLI commands (e.g., "How do I scale my app?")
- Work with deployments, addons, or pipelines
- Troubleshoot AppPack issues

## Example Usage

### Scaling Applications
```
You: Show me how to scale an AppPack web process
Claude: [Loads AppPack skill and provides detailed scaling instructions]
```

### Configuration Help
```
You: How do I set environment variables in AppPack?
Claude: [Loads AppPack skill and explains config commands]
```

### Troubleshooting
```
You: My AppPack health checks are failing with 404 errors
Claude: [Loads AppPack skill and helps diagnose the issue]
```

## What's Covered

### Core Capabilities
- Explaining AppPack architecture and concepts
- Guiding through deployment workflows
- Providing CLI command examples
- Fetching latest documentation
- Recommending best practices for security and operations

### Common Tasks
- Creating and configuring apps
- Setting up addons (databases, Redis, S3, SQS, SES)
- Managing environment variables and secrets
- Configuring custom domains and SSL
- Scaling applications (horizontal and vertical)
- Monitoring, logging, and troubleshooting
- Managing user access and permissions
- CI/CD pipeline configuration
- Cost optimization

### CLI Commands
Comprehensive reference for:
- Authentication (`apppack auth`)
- Resource creation (`apppack create`)
- App management (`apppack config`, `apppack ps`)
- Database operations (`apppack db`)
- Monitoring (`apppack logs`, `apppack events`, `apppack dash`)
- User management (`apppack access`, `apppack admins`)
- Cleanup (`apppack destroy`)

## Installation

This skill is already installed at `~/.claude/skills/apppack/`. It will be automatically discovered by Claude Code.

## Structure

```
~/.claude/skills/apppack/
├── SKILL.md       # Skill configuration and instructions
└── README.md      # This file
```

## Documentation

The skill always fetches fresh documentation from [docs.apppack.io](https://docs.apppack.io/) to ensure you get the latest information about:
- Tutorials and getting started guides
- How-to guides for specific tasks
- Technical explanations of how AppPack works
- Complete CLI command reference

## Updates

To update the skill, edit `SKILL.md` and restart Claude Code. Changes take effect immediately after restart.

## Learn More

- **AppPack Website**: https://apppack.io
- **AppPack Documentation**: https://docs.apppack.io/
- **CLI Reference**: https://docs.apppack.io/command-line-reference/

## About Skills

Skills are specialized capabilities that Claude Code loads automatically based on context. They provide domain expertise and help Claude assist you more effectively with specific technologies and tools.

For more information about skills, see the [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills).

