export interface StripeTransaction {
  transaction_type: "stripe";
  payment_id: string;
}
export interface MockTransaction {
  transaction_type: "mock";
}

export type TransactionData = StripeTransaction | MockTransaction;
