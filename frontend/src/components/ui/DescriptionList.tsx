export function DescriptionList({ children }: { children: React.ReactNode }) {
  return (
    <dl className="text-heading divide-y divide-default w-full">{children}</dl>
  );
}

export function DescriptionListRow({
  children,
}: {
  children: React.ReactNode;
}) {
  return <div className="flex flex-col pb-3 w-full">{children}</div>;
}

export function DescriptionListLabel({
  children,
}: {
  children: React.ReactNode;
}) {
  return <dl className="mb-1 flex">{children}</dl>;
}

export function DescriptionListData({
  children,
}: {
  children: React.ReactNode;
}) {
  return <dd className="mb-1">{children}</dd>;
}
