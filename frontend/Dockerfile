FROM node

WORKDIR /app

# Copy manifests
COPY package.json package-lock.json* ./

# If no lock file present fallback to npm install
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

COPY . .

# Build for production (recommended)
RUN npm run build

EXPOSE 3000
# SvelteKit preview (or use an adapter)
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "3000"]