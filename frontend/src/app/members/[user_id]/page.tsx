import MemberProfile from "@/components/features/members/MemberProfile";

interface MemberPageProps {
  params: Promise<{
    user_id: string;
  }>;
}

export default async function MemberPage({ params }: MemberPageProps) {
  const { user_id } = await params;
  const memberId = Number(user_id);

  // Avoid sending invalid route values to the backend
  if (!Number.isSafeInteger(memberId) || memberId < 1) {
    return (
      <main className="min-h-screen bg-gray-50 px-4 py-8">
        <div className="mx-auto max-w-3xl rounded-lg border border-red-200 bg-red-50 p-6">
          <h1 className="text-xl font-semibold text-red-800">
            Invalid member profile
          </h1>
          <p className="mt-2 text-red-700">
            The member ID in this link is not valid.
          </p>
        </div>
      </main>
    );
  }

  return <MemberProfile target={memberId} />;
}
