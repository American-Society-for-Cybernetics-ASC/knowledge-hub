# Frontend

This is the Next.js frontend root.

## Running

Ensure you created a `.env` based on `.env.example`.

### Development Build

From `/frontend`:

```bash
npm run dev
```

### Production Build

From `/frontend`:

```bash
npm run build
npm run start
```

## Type Checking

From `/frontend`:

```bash
npx tsc --noEmit
```

## Testing

### Run All Tests

From `/frontend`:

```bash
npm test
```

### Run Specific Test

From `/frontend`:

```bash
npm test -- src//file.test.tsx
```

## Linting

From `/frontend`:

```bash
npm run lint
```
