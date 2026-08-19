import Link from "next/link";
import MicrophoneIllustration from "@/components/MicrophoneIllustration";
import VoiceRagPlayground from "@/components/VoiceRagPlayground";
import TaskFeatureGrid from "@/components/TaskFeatureGrid";
import DeadlineCard from "@/components/DeadlineCard";
import SubmissionChecklist from "@/components/SubmissionChecklist";
import ResourceCards from "@/components/ResourceCards";

export default function VoiceEnabledRAGPage() {
  return (
    <div className="bg-[#F7F0DD] paper-texture min-h-screen py-10 lg:py-16">
      <div className="mx-auto max-w-5xl px-6 lg:px-10">
        
        {/* Breadcrumb Navigation */}
        <nav aria-label="Breadcrumb" className="mb-8">
          <ol className="flex flex-wrap items-center gap-2 text-xs font-bold tracking-widest text-[#8C7A58] uppercase">
            <li>
              <Link href="/" className="hover:text-[#E60067] transition-colors">
                HOME
              </Link>
            </li>
            <li aria-hidden="true" className="text-[#C5B182]">&gt;</li>
            <li>
              <Link href="/tasks" className="hover:text-[#E60067] transition-colors">
                TASKS
              </Link>
            </li>
            <li aria-hidden="true" className="text-[#C5B182]">&gt;</li>
            <li className="text-[#E60067]">VOICE-ENABLED RAG MODEL</li>
          </ol>
        </nav>

        {/* Task Title & Microphone Header */}
        <div className="grid gap-8 lg:grid-cols-12 lg:items-center">
          <div className="lg:col-span-7">
            <p className="label-upper text-[#E60067] font-bold tracking-widest text-xs">
              Task 02
            </p>
            <h1 className="editorial-heading mt-2 text-4xl sm:text-5xl lg:text-6xl text-[#073523] font-bold leading-[0.95]">
              Voice-Enabled
              <br />
              RAG Model
            </h1>
            <p className="mt-5 max-w-lg text-[15px] leading-relaxed text-[#567364] font-medium">
              Build a complete voice-to-answer system using
              Retrieval-Augmented Generation. Your pipeline should be fast,
              accurate, and safe.
            </p>
          </div>

          <div className="lg:col-span-5 flex justify-center lg:justify-end">
            <MicrophoneIllustration />
          </div>
        </div>

        {/* Live Interactive Voice & Text RAG Playground */}
        <div className="mt-12">
          <VoiceRagPlayground />
        </div>

        {/* Feature Grid */}
        <div className="mt-12">
          <TaskFeatureGrid />
        </div>

        {/* Deadline Card */}
        <div className="mt-10">
          <DeadlineCard />
        </div>

        {/* Submission Checklist */}
        <div className="mt-10">
          <SubmissionChecklist />
        </div>

        {/* Resources */}
        <div className="mt-10">
          <ResourceCards />
        </div>

      </div>
    </div>
  );
}
