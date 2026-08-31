// TODO: Implement member profile page
// GET /members/{user_id}
// PATCH /members/{user_id} - update a profile

interface MemberPageProps {
  params: {
    user_id: string;
  };
}

export default function MemberPage({ params }: MemberPageProps) {
  // TODO: Fetch member profile using params.user_id
  return <div>Member {params.user_id}</div>;
}
