# links.mirceanton.com

A minimalist "link in bio" style landing page that aggregates all my social media profiles and important links in one place.

## Tech Stack

- **Static Site Generator**: [Hugo](https://gohugo.io/) (extended)
- **Theme**: [Lynx](https://github.com/jpanther/lynx)
- **Styling**: Custom CSS with Dart Sass
- **Hosting**: GitHub Pages
- **CI/CD**: GitHub Actions

## Prerequisites

This project uses [mise](https://mise.jdx.dev/) for tool version management. Install mise and run:

```bash
mise install
```

## Local Development

```bash
# Start the development server
hugo server

# Build for production
hugo --minify
```

## Deployment

The site is automatically deployed to GitHub Pages via GitHub Actions:

- **On push to `main`**: Automatically builds and deploys
- **Manual trigger**: Available via workflow dispatch with optional dry-run mode
