import { useState, useEffect, type ReactElement } from "react";
import { ChevronLeft, ChevronRight, Copy } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";

function extractEmbeds(text: string): ReactElement {
  const embedStart = text.indexOf("<start_embed>");
  const embedEnd = text.indexOf("<end_embed>");

  if (embedStart !== -1 && embedEnd !== -1) {
    const before = text.slice(0, embedStart);
    const embedded = text.slice(embedStart + 13, embedEnd).trim();
    const after = text.slice(embedEnd + 11);

    return (
      <>
        {before && <p className="mb-2">{before}</p>}
        <pre className="bg-gray-100 p-4 rounded-md my-2 whitespace-pre-wrap font-mono text-sm">
          {embedded}
        </pre>
        {after && (
          <>
            <div className="mt-2" />
            {extractEmbeds(after)}
          </>
        )}
      </>
    );
  }

  return <p>{text}</p>;
}

// Render a single message in the chat
const ChatMessage = ({ role, content }) => {
  const roleColor =
    role === "user"
      ? "text-blue-500"
      : role === "system"
        ? "text-stone-500"
        : "text-gray-500";
  console.log({ role, roleColor });

  return (
    <div className={`mb-4 ${role === "assistant" ? "pl-4" : ""}`}>
      <div className={`font-semibold text-sm mb-1 ${roleColor}`}>
        {role.charAt(0).toUpperCase() + role.slice(1)}
      </div>
      <div className="text-gray-800">{extractEmbeds(content)}</div>
    </div>
  );
};

const ChatViewer = () => {
  const [currentOuterIndex, setCurrentOuterIndex] = useState(0);
  const [currentInnerIndex, setCurrentInnerIndex] = useState(0);
  const [data, setData] = useState([]);

  // Parse special tokens into structured chat data
  const parseChat = (text) => {
    const messages = [];
    const parts = text.split("<|start_header_id|>");

    // Skip the first part as it contains the initial tokens
    for (let i = 1; i < parts.length; i++) {
      const part = parts[i];
      const [role, ...contentParts] = part.split("<|end_header_id|>");
      const content = contentParts
        .join("")
        .split("<|eot_id|>")[0]
        .trim()
        .replace("&#x20;", " ");

      if (content) {
        messages.push({ role, content });
      }
    }

    return messages;
  };

  // Handle keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === "ArrowRight") {
        handleNext();
      } else if (e.key === "ArrowLeft") {
        handlePrevious();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [currentOuterIndex, currentInnerIndex, data]);

  const handleNext = () => {
    if (!data.length) return;

    if (
      currentInnerIndex <
      data[currentOuterIndex].evaluated_responses.length - 1
    ) {
      setCurrentInnerIndex(currentInnerIndex + 1);
    } else if (currentOuterIndex < data.length - 1) {
      setCurrentOuterIndex(currentOuterIndex + 1);
      setCurrentInnerIndex(0);
    }
  };

  const handlePrevious = () => {
    if (!data.length) return;

    if (currentInnerIndex > 0) {
      setCurrentInnerIndex(currentInnerIndex - 1);
    } else if (currentOuterIndex > 0) {
      setCurrentOuterIndex(currentOuterIndex - 1);
      setCurrentInnerIndex(
        data[currentOuterIndex - 1].evaluated_responses.length - 1,
      );
    }
  };

  const handleCopy = () => {
    if (!data.length) return;
    const currentResponse =
      data[currentOuterIndex].evaluated_responses[currentInnerIndex].response;
    navigator.clipboard.writeText(currentResponse);
  };

  // Load sample data
  useEffect(() => {
    const loadData = async () => {
      try {
        const response = await window.fs.readFile("data.json", {
          encoding: "utf8",
        });
        const jsonData = JSON.parse(response);
        setData(jsonData);
      } catch (error) {
        console.error("Error loading data:", error);
      }
    };

    loadData();
  }, []);

  if (!data.length) {
    return <div>Loading...</div>;
  }

  if (!data[currentOuterIndex]) {
    debugger;
  }
  const currentChatData =
    data[currentOuterIndex].evaluated_responses[currentInnerIndex];
  const messages = parseChat(currentChatData.response);

  const evaluationResult = currentChatData.evaluation_result;
  const evaluationResultColor =
    evaluationResult === "PASS"
      ? "text-green-400"
      : evaluationResult === "FAIL"
        ? "text-red-400"
        : "text-yellow-400";

  return (
    <div className="max-w-4xl mx-auto p-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div>
              Sample {currentOuterIndex + 1}.{currentInnerIndex + 1}
              <span
                className={
                  "ml-2 text-sm font-normal text-gray-500 " +
                  evaluationResultColor
                }
              >
                ({evaluationResult})
              </span>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={handlePrevious}
                className="p-2 rounded hover:bg-gray-100"
                disabled={currentOuterIndex === 0 && currentInnerIndex === 0}
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
              <button
                onClick={handleNext}
                className="p-2 rounded hover:bg-gray-100"
                disabled={
                  currentOuterIndex === data.length - 1 &&
                  currentInnerIndex ===
                  data[currentOuterIndex].evaluated_responses.length - 1
                }
              >
                <ChevronRight className="w-5 h-5" />
              </button>
              <button
                onClick={handleCopy}
                className="p-2 rounded hover:bg-gray-100"
                title="Copy original text"
              >
                <Copy className="w-5 h-5" />
              </button>
            </div>
          </CardTitle>
          <div className="text-sm text-gray-600">
            Criteria: {data[currentOuterIndex].criteria}
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {messages.map((msg, idx) => (
              <ChatMessage key={idx} {...msg} />
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ChatViewer;
