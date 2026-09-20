import { backendFetch } from "./client";
import { TransactionData } from "@/types/billing";

export interface ReadTransaction {
  id: string;
  payment_id: string;
  data: TransactionData;
}

export async function createTransaction(
  paymentId: string,
  provider: string,
): Promise<ReadTransaction> {
  return backendFetch<ReadTransaction>("/payments/transactions", {
    method: "POST",
    body: JSON.stringify({ payment_id: paymentId, provider_id: provider }),
  });
}

export function getTransaction(transactionId: string): Promise<ReadTransaction> {
  return backendFetch<ReadTransaction>(`/payments/transactions/${transactionId}`);
  // return Promise.resolve({
  //   id: transactionId,
  //   payment_id: "test-payment",
  //   data: { transaction_type: "mock", amount_value: 1000 },
  // }); Manually resolve getting a transaction for testing without auth/membership flow
}

export function confirmTransaction(transactionId: string): Promise<void> {
  return backendFetch<void>(`/payments/transactions/${transactionId}/confirm`, {
    method: "POST",
  })
  // return Promise.resolve(); Manually resolve transaction confirmation for testing without auth/membership flow
}