"use client";

import { useEffect, useRef, useState } from "react";
import { api, Character, Story, TimelineEvent } from "@/lib/api";

type Message = {
  id: string;
  role: "user" | "character";
  text: string;
};

export default function Home() {
  const [stories, setStories] = useState<Story[]>([]);
  const [story, setStory] = useState<Story | null>(null);

  const [characters, setCharacters] = useState<Character[]>([]);
  const [selectedCharacter, setSelectedCharacter] =
    useState<Character | null>(null);

  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  const [sequence, setSequence] = useState(1);

  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);

  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);

  const [worldSummary, setWorldSummary] = useState<any>(null);
  const [branchId, setBranchId] = useState("canon");
const [showExplore, setShowExplore] = useState(false);
const [showCharacterPicker, setShowCharacterPicker] = useState(false);
const [showEventEditor, setShowEventEditor] = useState(false);
const [showMemory, setShowMemory] = useState(false);
const [memoryFacts, setMemoryFacts] = useState<any[]>([]);
const [actionMessage, setActionMessage] = useState("");
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadStories();
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function loadStories() {
    try {
      setLoading(true);

      const data = await api.getStories();
      setStories(data);

      if (data.length > 0) {
        const demo =
          data.find((s) => s.id === "demo") ||
          data.find((s) =>
            s.title.toLowerCase().includes("attack on titan")
          ) ||
          data[0];

        await openStory(demo);
      }
    } catch (error) {
      console.error("Failed to load stories:", error);
    } finally {
      setLoading(false);
    }
  }

  async function openStory(nextStory: Story) {
    setBranchId("canon");
setShowExplore(false);
setShowCharacterPicker(false);
setShowEventEditor(false);
setShowMemory(false);
setActionMessage("");
    try {
      setStory(nextStory);

      const [chars, timelineData, summary] = await Promise.all([
        api.getCharacters(nextStory.id, "canon"),
        api.getTimeline(nextStory.id, "canon"),
        api.getWorldSummary(nextStory.id, "canon"),
      ]);

      setCharacters(chars);
      setTimeline(timelineData.events);
      setWorldSummary(summary);

      const startSequence =
        summary?.current_sequence ||
        timelineData.events[0]?.sequence ||
        1;

      setSequence(startSequence);

      const firstCharacter = chars[0] || null;
      setSelectedCharacter(firstCharacter);

      setMessages(
        firstCharacter
          ? [
              {
                id: `intro-${firstCharacter.id}`,
                role: "character",
                text:
                  firstCharacter.id === "eren"
                    ? "I'm Eren Yeager. Determined, impulsive, freedom-driven."
                    : `I'm ${firstCharacter.name}. ${
                        firstCharacter.description || ""
                      }`,
              },
            ]
          : []
      );
    } catch (error) {
      console.error("Failed to open story:", error);
    }
  }

  function selectTimeline(event: TimelineEvent) {
    setSequence(event.sequence);

    setMessages((current) => [
      ...current,
      {
        id: `timeline-${Date.now()}`,
        role: "character",
        text: `Timeline moved to Sequence ${event.sequence}: ${event.title}`,
      },
    ]);
  }

  function selectCharacter(character: Character) {
    setSelectedCharacter(character);

    setMessages([
      {
        id: `intro-${character.id}-${Date.now()}`,
        role: "character",
        text:
          character.id === "eren"
            ? "I'm Eren Yeager. Determined, impulsive, freedom-driven."
            : `I'm ${character.name}. ${
                character.description || "Ask me something."
              }`,
      },
    ]);
  }

  async function sendMessage() {
    if (!input.trim() || !story || !selectedCharacter || sending) {
      return;
    }

    const text = input.trim();

    setMessages((current) => [
      ...current,
      {
        id: `user-${Date.now()}`,
        role: "user",
        text,
      },
    ]);

    setInput("");
    setSending(true);

    try {
      const response = await api.chatWithCharacter(
        story.id,
        selectedCharacter.id,
        sequence,
        text,
        "canon"
      );

      if (response.success) {
        setMessages((current) => [
          ...current,
          {
            id: `character-${Date.now()}`,
            role: "character",
            text: response.output,
          },
        ]);
      } else {
        setMessages((current) => [
          ...current,
          {
            id: `error-${Date.now()}`,
            role: "character",
            text:
              response.errors?.join(", ") ||
              "The character could not respond.",
          },
        ]);
      }
    } catch (error) {
      console.error("Chat failed:", error);

      setMessages((current) => [
        ...current,
        {
          id: `error-${Date.now()}`,
          role: "character",
          text:
            "Connection to the narrative engine failed. Make sure the backend is running on port 8000.",
        },
      ]);
    } finally {
      setSending(false);
    }
  }

  async function uploadWorld() {
    if (!uploadFile || uploading) return;

    try {
      setUploading(true);

      const result = await api.uploadStory(
        uploadFile,
        uploadFile.name.replace(/\.[^/.]+$/, "")
      );

      const data = await api.getStories();
      setStories(data);

      const created =
        data.find((s) => s.id === result.story_id) ||
        data.find((s) => s.title === result.title);

      if (created) {
        await openStory(created);
      }

      setUploadFile(null);
    } catch (error) {
      console.error("Upload failed:", error);
      alert(
        "Upload failed. Check the backend terminal for the exact error."
      );
    } finally {
      setUploading(false);
    }
  }

  const currentEvent =
    timeline.find((event) => event.sequence === sequence) ||
    timeline[0];

  if (loading && !story) {
    return (
      <main className="min-h-screen bg-[#08080b] text-white flex items-center justify-center">
        <div className="text-purple-400 font-mono text-sm">
          Loading Re:World...
        </div>
      </main>
    );
  }

  return (
    <main className="h-screen overflow-hidden bg-[#08080b] text-white flex">
      {/* LEFT SIDEBAR */}
      <aside className="w-[274px] shrink-0 border-r border-[#25242d] bg-[#0b0b0f] p-5 flex flex-col">
        <div className="mb-5">
          <div className="text-xl font-bold">
            Re:World
          </div>

          <div className="text-[10px] text-[#777480] mt-1">
            Timeline-aware narrative engine
          </div>
        </div>

        <div className="text-[10px] uppercase tracking-[0.18em] text-[#777480] mb-2">
          Your Worlds
        </div>

        <div className="space-y-2">
          {stories.map((item) => (
            <button
              key={item.id}
              onClick={() => openStory(item)}
              className={`w-full text-left rounded-xl border p-4 transition ${
                story?.id === item.id
                  ? "border-purple-500/60 bg-[#211735]"
                  : "border-[#292832] bg-[#121218] hover:border-purple-500/40"
              }`}
            >
              <div className="font-semibold text-sm">
                {item.title}
              </div>

              <div className="text-[11px] text-[#88848f] mt-1">
                {item.description || "Story world"}
              </div>
            </button>
          ))}
        </div>

        {/* UPLOAD */}
        <div className="mt-3">
          <label className="w-full h-11 rounded-xl border border-dashed border-[#35333e] flex items-center justify-center text-xs text-[#aaa5b2] hover:border-purple-500/60 cursor-pointer transition">
            + Create / Upload World

            <input
              type="file"
              accept=".txt,.pdf,.docx"
              className="hidden"
              onChange={(e) =>
                setUploadFile(e.target.files?.[0] || null)
              }
            />
          </label>

          {uploadFile && (
            <div className="mt-2 rounded-lg border border-purple-500/30 bg-purple-500/10 p-2">
              <div className="text-[10px] text-purple-300 truncate">
                {uploadFile.name}
              </div>

              <button
                onClick={uploadWorld}
                disabled={uploading}
                className="mt-2 w-full rounded-md bg-purple-600 py-2 text-xs font-semibold hover:bg-purple-500 disabled:opacity-50"
              >
                {uploading ? "Analyzing..." : "Upload World"}
              </button>
            </div>
          )}
        </div>

        {/* CHARACTERS */}
        <div className="text-[10px] uppercase tracking-[0.18em] text-[#777480] mt-7 mb-2">
          Characters
        </div>

        <div className="space-y-2 overflow-y-auto min-h-0">
          {characters.map((character) => (
            <button
              key={character.id}
              onClick={() => selectCharacter(character)}
              className={`w-full text-left rounded-xl border px-3 py-3 transition ${
                selectedCharacter?.id === character.id
                  ? "border-purple-500/60 bg-[#211735]"
                  : "border-[#292832] bg-[#121218] hover:border-purple-500/40"
              }`}
            >
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">
                  {character.name}
                </span>

                <span className="h-2 w-2 rounded-full bg-emerald-400" />
              </div>

              <div className="text-[10px] text-[#777480] mt-1">
                {character.current_location || "Unknown"}
              </div>
            </button>
          ))}
        </div>

        {/* FULL TIMELINE */}
        <div className="text-[10px] uppercase tracking-[0.18em] text-[#777480] mt-6 mb-2">
          Timeline
        </div>

        <div className="flex-1 min-h-0 overflow-y-auto pr-1">
          <div className="space-y-2">
            {timeline.length === 0 ? (
              <div className="text-[10px] text-[#55515d]">
                No timeline events found.
              </div>
            ) : (
              timeline.map((event) => {
                const active = event.sequence === sequence;

                return (
                  <button
                    key={event.id}
                    onClick={() => selectTimeline(event)}
                    className={`w-full text-left rounded-xl border p-3 transition ${
                      active
                        ? "border-purple-500/60 bg-[#211735]"
                        : "border-[#292832] bg-[#121218] hover:border-purple-500/40"
                    }`}
                  >
                    <div className="flex items-start gap-2">
                      <span
                        className={`mt-1.5 h-2 w-2 rounded-full shrink-0 ${
                          active
                            ? "bg-purple-400"
                            : "bg-[#55515d]"
                        }`}
                      />

                      <div className="min-w-0">
                        <div className="text-xs font-medium">
                          {event.title}
                        </div>

                        <div className="text-[9px] text-[#777480] mt-1">
                          Sequence {event.sequence}
                        </div>

                        <div className="text-[9px] text-[#55515d] mt-1 line-clamp-2">
                          {event.description}
                        </div>
                      </div>
                    </div>
                  </button>
                );
              })
            )}
          </div>
        </div>
      </aside>

      {/* CENTER */}
      <section className="flex-1 min-w-0 flex flex-col">
        <header className="h-[100px] shrink-0 border-b border-[#25242d] flex flex-col items-center justify-center">
          <div className="text-[9px] uppercase tracking-[0.28em] text-purple-400">
            {story?.title || "RE:WORLD"}
          </div>

          <h1 className="text-2xl font-bold mt-1">
            Talk to {selectedCharacter?.name || "Character"}
          </h1>

          <div className="text-xs text-[#777480] mt-1">
            {selectedCharacter?.personality?.slice(0, 3).join(", ") ||
              "Timeline-aware character simulation"}
          </div>
        </header>

        {/* CURRENT TIMELINE POINT */}
        <div className="border-b border-[#25242d] px-6 py-2 bg-[#0b0b0f]">
          <div className="max-w-3xl mx-auto flex items-center justify-between">
            <div>
              <div className="text-[9px] uppercase tracking-[0.15em] text-[#777480]">
                Current timeline point
              </div>

              <div className="text-xs font-medium mt-1">
                Sequence {sequence}
                {currentEvent ? ` — ${currentEvent.title}` : ""}
              </div>
            </div>

            <div className="text-[9px] text-purple-400">
              Character knowledge cutoff: {sequence}
            </div>
          </div>
        </div>

        {/* CHAT */}
        <div className="flex-1 overflow-y-auto px-10 py-7">
          <div className="max-w-3xl mx-auto space-y-5">
            {messages.map((message) =>
              message.role === "user" ? (
                <div
                  key={message.id}
                  className="flex justify-end"
                >
                  <div className="max-w-[70%] rounded-xl bg-purple-600 px-5 py-3 text-sm">
                    {message.text}
                  </div>
                </div>
              ) : (
                <div
                  key={message.id}
                  className="max-w-[78%] rounded-xl border border-[#292832] bg-[#121218] px-5 py-4"
                >
                  <div className="text-[11px] font-semibold text-purple-400 mb-2">
                    {selectedCharacter?.name || "Character"}
                  </div>

                  <div className="text-sm leading-6 text-[#e4e1e8]">
                    {message.text}
                  </div>
                </div>
              )
            )}

            {sending && (
              <div className="max-w-[78%] rounded-xl border border-[#292832] bg-[#121218] px-5 py-4">
                <div className="text-xs text-purple-400">
                  {selectedCharacter?.name} is thinking...
                </div>
              </div>
            )}

            <div ref={chatEndRef} />
          </div>
        </div>

        {/* INPUT */}
        <div className="shrink-0 border-t border-[#25242d] px-7 py-5">
          <div className="max-w-3xl mx-auto">
            <div className="flex gap-2 mb-3">
              <button className="rounded-full border border-[#2b2933] px-3 py-1.5 text-[10px] text-[#aaa5b2]">
                Explore this world
              </button>

              <button className="rounded-full border border-[#2b2933] px-3 py-1.5 text-[10px] text-[#aaa5b2]">
                Talk to another character
              </button>

              <button className="rounded-full border border-[#2b2933] px-3 py-1.5 text-[10px] text-[#aaa5b2]">
                Change an event
              </button>
            </div>

            <div className="flex rounded-xl border border-[#302d3a] bg-[#121218] p-2">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                  }
                }}
                placeholder={`Talk to ${
                  selectedCharacter?.name || "character"
                }...`}
                className="flex-1 bg-transparent px-3 py-3 text-sm outline-none text-white placeholder:text-[#55515d]"
              />

              <button
                onClick={sendMessage}
                disabled={!input.trim() || sending}
                className="rounded-lg bg-purple-600 px-5 text-sm font-semibold hover:bg-purple-500 disabled:opacity-40"
              >
                {sending ? "..." : "Send"}
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* RIGHT SIDEBAR */}
      <aside className="w-[260px] shrink-0 border-l border-[#25242d] bg-[#0b0b0f] p-5 flex flex-col">
        <div className="text-[10px] uppercase tracking-[0.18em] text-[#777480] mb-3">
          World State
        </div>

        <div className="space-y-2">
          <StateCard
            label="Location"
            value={
              selectedCharacter?.current_location || "Unknown"
            }
          />

          <StateCard
            label="Current Point"
            value={
              currentEvent
                ? `Sequence ${sequence}`
                : `Sequence ${sequence}`
            }
          />

          <StateCard
            label="Event"
            value={currentEvent?.title || "Unknown"}
          />

          <StateCard
            label="Timeline"
            value="Canon"
          />

          <StateCard
            label="World"
            value={story?.title || "Unknown"}
          />

          {worldSummary && (
            <StateCard
              label="Characters"
              value={String(worldSummary.character_count)}
            />
          )}
        </div>

        {/* WHAT IF */}
        <div className="mt-auto rounded-xl border border-purple-500/30 bg-[#171020] p-4">
          <div className="text-sm font-semibold text-purple-300">
            ✨ What-if Mode
          </div>

          <div className="text-[11px] text-[#8e8799] mt-2 leading-5">
            Create an alternate timeline by changing an event.
          </div>

          <button
            onClick={async () => {
              if (!story) return;

              const change = window.prompt(
                `What should change at Sequence ${sequence}?`
              );

              if (!change) return;

              try {
                await api.createBranch(
                  story.id,
                  sequence,
                  change,
                  "canon"
                );

                alert("Alternate branch created.");
              } catch (error) {
                console.error(error);
                alert("Could not create branch.");
              }
            }}
            className="mt-3 w-full rounded-lg border border-purple-500/40 py-2 text-xs text-purple-300 hover:bg-purple-500/10"
          >
            Create Branch
          </button>
        </div>
      </aside>
    </main>
  );
}

function StateCard({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-xl border border-[#292832] bg-[#121218] px-4 py-3">
      <div className="text-[9px] uppercase tracking-[0.16em] text-[#777480]">
        {label}
      </div>

      <div className="text-sm font-medium mt-1">
        {value}
      </div>
    </div>
  );
}