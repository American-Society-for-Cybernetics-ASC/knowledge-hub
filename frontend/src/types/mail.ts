export interface FailedEmail {
  id: number;
  last_sent: string;
  retries: number;
  error?: string;
  email: {
    sender: string;
    recipients: string[];
    subject: string;
  };
}

export interface GmailAppPasswordMailProvider {
  provider_type: "gmail_app_password";
  google_username: string;
  app_password: string;
}

export type MailProvider = GmailAppPasswordMailProvider;

export interface ReadMailSender {
  id: string;
  name: string;
  description: string;
  provider: MailProvider;
}

export type PatchMailSender = Partial<Omit<ReadMailSender, "id">>;
export type PostMailSender = Omit<ReadMailSender, "id">;

export interface TestMailProvider {
  provider: MailProvider;
  email: string;
}
