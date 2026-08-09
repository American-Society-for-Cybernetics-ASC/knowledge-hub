// TODO: Implement membership detail page
// GET /membership/{membership_id}
// POST /membership/{membership_id}/cancel
// /membership/{membership_id}/uncancel

interface MembershipPageProps {
    params: {
        membership_id: string;
    };
}

export default function MembershipPage({params}: MembershipPageProps) {
    // TODO: Fetch membership using params.membership_id
    return <div>Membership {params.membership_id}</div>;
}