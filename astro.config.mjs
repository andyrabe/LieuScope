// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// Sans nom de domaine, le site vit sous https://<compte>.github.io/<depot>/.
// Quand le domaine arrivera : public/CNAME, site: 'https://<domaine>', base: '/'.
export default defineConfig({
  site: 'https://andyrabe.github.io',
  base: '/LieuScope',
  trailingSlash: 'ignore',
  output: 'static',
  integrations: [sitemap()],
  build: { format: 'directory' },
});
