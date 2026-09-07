export interface StripeTransaction {
    payment_id: string;
    transaction_type: "stripe";
    amount_value: number;
    currency: string;
}
export interface MockTransaction {
  transaction_type: "mock";
  amount_value: number;
}

export type TransactionData = StripeTransaction | MockTransaction;

export interface PaymentRecord {
    payment_id: number;
    date: string;
    status: string;
    kind: string;
    transaction: TransactionData;
}