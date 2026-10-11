export const formatAmount = (cents: number) =>
  new Intl.NumberFormat("en-US", { style: "currency", currency: "usd" }).format(
    cents / 100,
  );
