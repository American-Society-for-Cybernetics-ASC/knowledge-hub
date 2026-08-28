"use client";

import { useEffect, useState, type FormEvent } from "react";
import { getMyProfile, updateMyProfile } from "@/lib/api/members";
import type { MemberProfile, ProfileUpdate } from "@/types/member"; 

function toCSV(values: string[] | null): string {
    return values?.join(", ") ?? "";
}

function toStringList(value: string): string[] {
    return [...new Set(
        value
            .split(",")
            .map((item) => item.trim())
            .filter(Boolean),
    )];
}

export default function EditMyProfilePage() {
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
    
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");

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
                setResearchInterests(
                    toCSV(data.content.research_interests)
                );
                setExpertise(toCSV(data.content.expertise));
                setTags(toCSV(data.tags));
            } catch (err: unknown) {
                setError(
                    err instanceof Error 
                    ? err.message
                    : "Unable to load your profile",
                );
            } finally {
                setLoading(false);
            }
        }

        void loadProfile();
    }, []);

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
        
        setSaving(true);

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
        };

        try {
            const updatedProfile = await updateMyProfile(update);
            setProfile(updatedProfile);
            setSuccess("Your profile has been saved.");
        } catch (err: unknown) {
            setError(
                err instanceof Error
                ? err.message 
                : "Unable to save your profile. Please try again.",
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
                    <div className="bg-red-50 text-red-700 p-3 rounded text-sm">
                        {error || "Your profile could not be loaded."}
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 py-8 px-4">
            <div className="max-w-2xl mx-auto bg-white rounded-lg shadow p-8">
                <h1 className="text-2xl font-bold mb-6">Edit my profile</h1>

                {error && (
                    <div className="bg-red-50 text-red-700 p-3 rounded mb-4 text-sm">
                        {error}
                    </div>
                )}

                {success && (
                    <div className="bg-green-50 text-green-700 p-3 rounded mb-4 text-sm">
                        {success}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label htmlFor="display-name" className="block text-sm font-medium text-gray-700 mb-1">
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
                        <label htmlFor="pronouns" className="block text-sm font-medium text-gray-700 mb-1">
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
                        <label htmlFor="location" className="block text-sm font-medium text-gray-700 mb-1">
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
                        <label htmlFor="website" className="block text-sm font-medium text-gray-700 mb-1">
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
                        <label htmlFor="orcid" className="block text-sm font-medium text-gray-700 mb-1">
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
                        <label htmlFor="personal-statement" className="block text-sm font-medium text-gray-700 mb-1">
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
                        <label htmlFor="research-interests" className="block text-sm font-medium text-gray-700 mb-1">
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
                        <label htmlFor="expertise" className="block text-sm font-medium text-gray-700 mb-1">
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
                        <label htmlFor="tags" className="block text-sm font-medium text-gray-700 mb-1">
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
                        <p className="mt-1 text-xs text-gray-500">Separate tags with commas</p>
                    </div>

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