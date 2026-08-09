// TODO: Implement submissions list page
// GET /knowledge-hub/{repository_id}/submissions
// POST /knowledge-hub/{repository_id} - make a submission

interface SubmissionsPageProps {
    params: {
        repository_id: string;
    };
}

export default function SubmissionsPage({params}: SubmissionsPageProps) {
    // TODO: Fetch submissions using params.repository_id
    return <div>Submissions for Repository {params.repository_id}</div>;
}