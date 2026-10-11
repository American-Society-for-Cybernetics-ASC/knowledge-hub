"use client";

import { useEffect, useState, type FormEvent } from "react";
import { getMyProfile, updateMyProfile } from "@/lib/api/members";
import type {
  MemberProfile,
  ProfileUpdate,
  Affiliation,
  ProfilePublication,
} from "@/types/member";
import { useRouter } from "next/navigation";
import InlineError from "@/components/layout/InlineError";
import { useAddError } from "@/components/layout/ErrorContext";
import { getErrorMessage } from "@/lib/errors";

// Convert list fields from API into CSV
function toCSV(values: string[] | null): string {
  return values?.join(", ") ?? "";
}

// Parse CSV input
function toStringList(value: string): string[] {
  return [
    ...new Set(
      value
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean),
    ),
  ];
}

interface AffiliationForm {
  organisation: string;
  role: string;
  start_year: string;
  end_year: string;
}

interface PublicationForm {
  title: string;
  year: string;
  doi: string;
  url: string;
}

function emptyAffiliation(): AffiliationForm {
  return {
    organisation: "",
    role: "",
    start_year: "",
    end_year: "",
  };
}

function emptyPublication(): PublicationForm {
  return {
    title: "",
    year: "",
    doi: "",
    url: "",
  };
}

function affiliationToForm(affiliation: Affiliation): AffiliationForm {
  return {
    organisation: affiliation.organisation,
    role: affiliation.role ?? "",
    start_year: affiliation.start_year?.toString() ?? "",
    end_year: affiliation.end_year?.toString() ?? "",
  };
}

function publicationToForm(publication: ProfilePublication): PublicationForm {
  return {
    title: publication.title,
    year: publication.year?.toString() ?? "",
    doi: publication.doi ?? "",
    url: publication.url ?? "",
  };
}

function parseYear(value: string, label: string): number | null {
  const trimmedValue = value.trim();

  if (!trimmedValue) {
    return null;
  }

  const year = Number(trimmedValue);

  if (!Number.isInteger(year) || year < 1000 || year > 2100) {
    throw new Error(`${label} must be a year between 1000 and 2100`);
  }

  return year;
}

function parseUrl(value: string, label: string): string | null {
  const trimmedValue = value.trim();

  if (!trimmedValue) {
    return null;
  }

  try {
    const url = new URL(trimmedValue);

    if (url.protocol !== "http:" && url.protocol !== "https:") {
      throw new Error();
    }

    return trimmedValue;
  } catch {
    throw new Error(`${label} must be a valid HTTP or HTTPS URL.`);
  }
}

function parseDoi(value: string): string | null {
  const doi = value.trim();

  if (!doi) {
    return null;
  }

  if (!/^10\.\d{4,9}\/\S+$/.test(doi)) {
    throw new Error("DOI must start with 10. followed by a valid DOI value.");
  }

  return doi;
}

export default function EditMyProfilePage() {
  const router = useRouter();
  const [profile, setProfile] = useState<MemberProfile | null>(null);
  const [displayName, setDisplayName] = useState("");
  const [pronouns, setPronouns] = useState("");
  const [location, setLocation] = useState("");
  const [website, setWebsite] = useState("");
  const [orcid, setOrcid] = useState("");
  const [personalStatement, setPersonalStatement] = useState("");
  const [researchInterests, setResearchInterests] = useState("");
  const [expertise, setExpertise] = useState("");
  const [tags, setTags] = useState("");
  const [affiliations, setAffiliations] = useState<AffiliationForm[]>([]);
  const [publications, setPublications] = useState<PublicationForm[]>([]);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const addError = useAddError();

  // Load current member profile when the page is loaded
  useEffect(() => {
    async function loadProfile() {
      try {
        const data = await getMyProfile();

        setProfile(data);
        setDisplayName(data.content.identity.display_name ?? "");
        setPronouns(data.content.identity.pronouns ?? "");
        setLocation(data.content.identity.location ?? "");
        setWebsite(data.content.identity.website ?? "");
        setOrcid(data.content.identity.orcid ?? "");
        setPersonalStatement(data.content.personal_statement ?? "");
        setResearchInterests(toCSV(data.content.research_interests));
        setExpertise(toCSV(data.content.expertise));
        setTags(toCSV(data.tags));

        const affiliationsMetadata = data.content.metadata.affiliations;
        setAffiliations(
          affiliationsMetadata?.type === "affiliations"
            ? affiliationsMetadata.value.map(affiliationToForm)
            : [],
        );

        const publicationsMetadata = data.content.metadata.publications;
        setPublications(
          publicationsMetadata?.type === "publications"
            ? publicationsMetadata.value.map(publicationToForm)
            : [],
        );
      } catch (err: unknown) {
        addError(getErrorMessage(err, "Unable to load your profile"));
      } finally {
        setLoading(false);
      }
    }

    void loadProfile();
  }, []);

  function updateAffiliation(
    index: number,
    field: keyof AffiliationForm,
    value: string,
  ) {
    setAffiliations((currentAffiliations) =>
      currentAffiliations.map((affiliation, currentIndex) =>
        currentIndex === index
          ? { ...affiliation, [field]: value }
          : affiliation,
      ),
    );
  }

  function removeAffiliation(index: number) {
    setAffiliations((currentAffiliations) =>
      currentAffiliations.filter((_, currentIndex) => currentIndex !== index),
    );
  }

  function updatePublication(
    index: number,
    field: keyof PublicationForm,
    value: string,
  ) {
    setPublications((currentPublications) =>
      currentPublications.map((publication, currentIndex) =>
        currentIndex === index
          ? { ...publication, [field]: value }
          : publication,
      ),
    );
  }

  function removePublication(index: number) {
    setPublications((currentPublications) =>
      currentPublications.filter((_, currentIndex) => currentIndex !== index),
    );
  }

  // Handle form submission
  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setSuccess("");

    const researchInterestsList = toStringList(researchInterests);
    const expertiseList = toStringList(expertise);
    const tagsList = toStringList(tags);

    if (researchInterestsList.length > 30) {
      setError("You can only enter up to 30 research interests.");
      return;
    }

    if (expertiseList.length > 30) {
      setError("You can only enter up to 30 expertise.");
      return;
    }

    if (tagsList.length > 50) {
      setError("You can only enter up to 50 tags.");
      return;
    }

    if (affiliations.length > 20) {
      setError("You can only enter up to 20 affiliations.");
      return;
    }

    if (publications.length > 50) {
      setError("You can only enter up to 50 publications.");
      return;
    }

    let affiliationValues: Affiliation[];
    let publicationValues: ProfilePublication[];

    try {
      affiliationValues = affiliations.map((affiliation, index) => {
        const organisation = affiliation.organisation.trim();

        if (!organisation) {
          throw new Error(`Affiliation ${index + 1} needs an organisation.`);
        }

        const startYear = parseYear(
          affiliation.start_year,
          `Affiliation ${index + 1} start year`,
        );
        const endYear = parseYear(
          affiliation.end_year,
          `Affiliation ${index + 1} end year`,
        );

        if (startYear && endYear && endYear < startYear) {
          throw new Error(
            `Affiliation ${index + 1} end year cannot be before the start year.`,
          );
        }

        return {
          organisation,
          role: affiliation.role.trim() || null,
          start_year: startYear,
          end_year: endYear,
        };
      });

      publicationValues = publications.map((publication, index) => {
        const title = publication.title.trim();

        if (!title) {
          throw new Error(`Publication ${index + 1} needs a title.`);
        }

        return {
          title,
          year: parseYear(publication.year, `Publication ${index + 1} year`),
          doi: parseDoi(publication.doi),
          url: parseUrl(publication.url, `Publication ${index + 1} URL`),
        };
      });
    } catch (err: unknown) {
      setError(
        getErrorMessage(
          err,
          "Please check your affiliations and publications.",
        ),
      );
      return;
    }

    // Start saving process
    setSaving(true);

    // Construct update payload
    const update: ProfileUpdate = {
      identity: {
        display_name: displayName || null,
        pronouns: pronouns || null,
        location: location || null,
        website: website || null,
        orcid: orcid || null,
      },
      personal_statement: personalStatement || null,
      research_interests: toStringList(researchInterests),
      expertise: toStringList(expertise),
      tags: toStringList(tags),
      metadata: {
        affiliations: {
          type: "affiliations",
          value: affiliationValues,
        },
        publications: {
          type: "publications",
          value: publicationValues,
        },
      },
    };

    // Send the update to backend
    try {
      const updatedProfile = await updateMyProfile(update);
      setProfile(updatedProfile);
      setSuccess("Your profile has been saved.");
      router.push("/members/me");
    } catch (err: unknown) {
      addError(
        getErrorMessage(err, "Unable to save your profile. Please try again."),
      );
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <p className="text-gray-600">Loading your profile...</p>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full bg-white rounded-lg shadow p-8">
          <h1 className="text-2xl font-bold mb-4">Edit my profile</h1>
          <InlineError message={error || "Your profile could not be loaded."} />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-2xl mx-auto bg-white rounded-lg shadow p-8">
        <h1 className="text-2xl font-bold mb-6">Edit my profile</h1>

        <InlineError message={error} />

        {success && (
          <div className="bg-green-50 text-green-700 p-3 rounded mb-4 text-sm">
            {success}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label
              htmlFor="display-name"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Display Name
            </label>
            <input
              id="display-name"
              type="text"
              value={displayName}
              onChange={(event) => setDisplayName(event.target.value)}
              maxLength={100}
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label
              htmlFor="pronouns"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Pronouns
            </label>
            <input
              id="pronouns"
              type="text"
              value={pronouns}
              onChange={(event) => setPronouns(event.target.value)}
              maxLength={100}
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label
              htmlFor="location"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Location
            </label>
            <input
              id="location"
              type="text"
              value={location}
              onChange={(event) => setLocation(event.target.value)}
              maxLength={150}
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label
              htmlFor="website"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Website
            </label>
            <input
              id="website"
              type="url"
              value={website}
              onChange={(event) => setWebsite(event.target.value)}
              placeholder="https://example.com"
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label
              htmlFor="orcid"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              ORCID
            </label>
            <input
              id="orcid"
              type="text"
              value={orcid}
              onChange={(event) => setOrcid(event.target.value)}
              placeholder="0000-0000-0000-0000"
              pattern="\d{4}-\d{4}-\d{4}-\d{3}[\dX]"
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label
              htmlFor="personal-statement"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Personal Statement
            </label>
            <textarea
              id="personal-statement"
              value={personalStatement}
              onChange={(event) => setPersonalStatement(event.target.value)}
              maxLength={5000}
              rows={5}
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label
              htmlFor="research-interests"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Research Interests
            </label>
            <input
              id="research-interests"
              type="text"
              value={researchInterests}
              onChange={(event) => setResearchInterests(event.target.value)}
              placeholder="Cybernetics"
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="mt-1 text-xs text-gray-500">Separate with commas</p>
          </div>

          <div>
            <label
              htmlFor="expertise"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Expertise
            </label>
            <input
              id="expertise"
              type="text"
              value={expertise}
              onChange={(event) => setExpertise(event.target.value)}
              placeholder="Cybernetics, Research, Programming"
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="mt-1 text-xs text-gray-500">Separate with commas</p>
          </div>

          <div>
            <label
              htmlFor="tags"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Tags
            </label>
            <input
              id="tags"
              type="text"
              value={tags}
              onChange={(event) => setTags(event.target.value)}
              placeholder="cybernetics, research"
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="mt-1 text-xs text-gray-500">
              Separate tags with commas
            </p>
          </div>

          <section className="border-t border-gray-200 pt-6">
            <div className="flex items-center justify-between gap-4">
              <div>
                <h2 className="text-lg font-semibold text-gray-900">
                  Affiliations
                </h2>
                <p className="mt-1 text-sm text-gray-600">
                  Add organisations you are currently or previously affiliated
                  with.
                </p>
              </div>

              <button
                type="button"
                onClick={() =>
                  setAffiliations((current) => [...current, emptyAffiliation()])
                }
                disabled={affiliations.length >= 20}
                className="rounded border border-gray-300 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
              >
                Add affiliation
              </button>
            </div>

            <div className="mt-4 space-y-4">
              {affiliations.map((affiliation, index) => (
                <div
                  key={index}
                  className="rounded-lg border border-gray-200 p-4"
                >
                  <div className="grid gap-4 sm:grid-cols-2">
                    <input
                      type="text"
                      value={affiliation.organisation}
                      onChange={(event) =>
                        updateAffiliation(
                          index,
                          "organisation",
                          event.target.value,
                        )
                      }
                      maxLength={200}
                      placeholder="Organisation *"
                      className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
                    />

                    <input
                      type="text"
                      value={affiliation.role}
                      onChange={(event) =>
                        updateAffiliation(index, "role", event.target.value)
                      }
                      maxLength={150}
                      placeholder="Role"
                      className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
                    />

                    <input
                      type="number"
                      value={affiliation.start_year}
                      onChange={(event) =>
                        updateAffiliation(
                          index,
                          "start_year",
                          event.target.value,
                        )
                      }
                      min={1000}
                      max={2100}
                      placeholder="Start year *"
                      className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
                    />

                    <input
                      type="number"
                      value={affiliation.end_year}
                      onChange={(event) =>
                        updateAffiliation(index, "end_year", event.target.value)
                      }
                      min={1000}
                      max={2100}
                      placeholder="End year"
                      className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
                    />
                  </div>

                  <button
                    type="button"
                    onClick={() => removeAffiliation(index)}
                    className="mt-4 text-sm font-medium text-red-700 hover:underline"
                  >
                    Remove affiliation
                  </button>
                </div>
              ))}
            </div>
          </section>

          <section className="border-t border-gray-200 pt-6">
            <div className="flex items-center justify-between gap-4">
              <div>
                <h2 className="text-lg font-semibold text-gray-900">
                  Publications
                </h2>
                <p className="mt-1 text-sm text-gray-600">
                  Add publications you like displayed on your profile.
                </p>
              </div>

              <button
                type="button"
                onClick={() =>
                  setPublications((current) => [...current, emptyPublication()])
                }
                disabled={publications.length >= 50}
                className="rounded border border-gray-300 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
              >
                Add publication
              </button>
            </div>

            <div className="mt-4 space-y-4">
              {publications.map((publication, index) => (
                <div
                  key={index}
                  className="rounded-lg border border-gray-200 p-4"
                >
                  <div className="grid gap-4 sm:grid-cols-2">
                    <input
                      type="text"
                      value={publication.title}
                      onChange={(event) =>
                        updatePublication(index, "title", event.target.value)
                      }
                      maxLength={500}
                      placeholder="Publication title *"
                      className="w-full border border-gray-300 rounded px-3 py-2 text-sm sm:col-span-2"
                    />

                    <input
                      type="number"
                      value={publication.year}
                      onChange={(event) =>
                        updatePublication(index, "year", event.target.value)
                      }
                      min={1000}
                      max={2100}
                      placeholder="Publication year *"
                      className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
                    />

                    <input
                      type="text"
                      value={publication.doi}
                      onChange={(event) =>
                        updatePublication(index, "doi", event.target.value)
                      }
                      maxLength={255}
                      placeholder="DOI, e.g. 10.1234/example"
                      className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
                    />

                    <input
                      type="url"
                      value={publication.url}
                      onChange={(event) =>
                        updatePublication(index, "url", event.target.value)
                      }
                      placeholder="https://example.com/publication"
                      className="w-full border border-gray-300 rounded px-3 py-2 text-sm sm:col-span-2"
                    />
                  </div>

                  <button
                    type="button"
                    onClick={() => removePublication(index)}
                    className="mt-4 text-sm font-medium text-red-700 hover:underline"
                  >
                    Remove publication
                  </button>
                </div>
              ))}
            </div>
          </section>

          <button
            type="submit"
            disabled={saving}
            className="w-full bg-blue-600 text-white py-2 rounded font-medium hover:bg-blue-700 disabled:opacity-50"
          >
            {saving ? "Saving..." : "Save profile"}
          </button>
        </form>
      </div>
    </div>
  );
}
