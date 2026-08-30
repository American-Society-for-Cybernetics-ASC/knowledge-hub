// TODO: Implement submission detail page
// GET /knowledge-hub/{repository_id}/submissions/{submission_id}

interface SubmissionPageProps {
  params: {
    repository_id: string;
    submission_id: string;
  };
}

export default function SubmissionPage({ params }: SubmissionPageProps) {
  // TODO: Fetch submission using params.repository_id and params.submission_id
  return <div>Submission {params.submission_id}</div>;
}
