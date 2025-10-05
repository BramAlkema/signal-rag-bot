# GitHub Pages Website Setup

## Enabling GitHub Pages

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Pages**
3. Under "Build and deployment":
   - **Source**: Deploy from a branch
   - **Branch**: `main`
   - **Folder**: `/docs_website`
4. Click **Save**

GitHub will automatically build and deploy your site within 1-2 minutes.

## Your Website URL

After deployment, your site will be available at:
```
https://<username>.github.io/<repository-name>/
```

For example:
```
https://bramalkem.github.io/signal-rag-bot/
```

## Local Testing

To test the website locally before pushing:

```bash
cd docs_website
python3 -m http.server 8000
```

Then open: http://localhost:8000

## File Structure

```
docs_website/
├── index.html      # Main website content
├── style.css       # Styles and animations
├── script.js       # Tab switching and interactions
└── README.md       # This file
```

## Features

- ✅ Fully responsive (mobile, tablet, desktop)
- ✅ Modern gradient design
- ✅ Animated cards and sections
- ✅ Tab-based quick start guides
- ✅ Smooth scrolling navigation
- ✅ No external dependencies (pure HTML/CSS/JS)

## Customization

### Colors

Edit the CSS variables in `style.css`:

```css
:root {
    --primary: #6366f1;
    --secondary: #8b5cf6;
    --accent: #ec4899;
    /* ... */
}
```

### Content

Edit `index.html` to update:
- Project description
- Features
- Deployment options
- Documentation links
- Tech stack

### Tabs

Add new quick start tabs in `index.html`:

```html
<button class="tab-button" data-tab="new-tab">New Platform</button>
<!-- ... -->
<div id="new-tab" class="tab-content">
    <pre>Your setup commands here</pre>
</div>
```

## GitHub Pages Configuration

After enabling Pages, you can optionally:

1. **Custom Domain**: Add a custom domain in Settings → Pages
2. **HTTPS**: GitHub Pages automatically provides HTTPS
3. **404 Page**: Create `404.html` for custom error page
4. **Analytics**: Add Google Analytics or similar

## Updating the Website

1. Make changes to files in `docs_website/`
2. Commit and push:
   ```bash
   git add docs_website/
   git commit -m "Update website"
   git push origin main
   ```
3. GitHub Pages will automatically rebuild (1-2 minutes)

## Support

For GitHub Pages documentation:
https://docs.github.com/en/pages
