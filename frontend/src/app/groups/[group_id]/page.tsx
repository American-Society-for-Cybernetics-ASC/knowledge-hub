// TODO: Implement group members page
// GET /groups/{group_id}/members
// POST /groups/{group_id}/members/{member_id}/add - add a user to a group
// POST /groups/{group_id}/members/{member_id}/kick - kick a user from a group

interface GroupPageProps {
  params: {
    group_id: string;
  };
}

export default function GroupPage({ params }: GroupPageProps) {
  // TODO: Fetch group members using params.group_id
  return <div>Group {params.group_id}</div>;
}
