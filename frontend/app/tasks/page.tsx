import Link from "next/link";

const tasks = [
  {
    slug: "voice-enabled-rag",
    number: "02",
    title: "Voice-Enabled RAG Model",
    description:
      "Build a complete voice-to-answer system using Retrieval-Augmented Generation.",
    deadline: "13 AUG 2026",
    status: "OPEN",
  },
];

export default function TasksPage() {
  return (
    <div className="paper-texture min-h-screen py-12 lg:py-16">
      <div className="mx-auto max-w-7xl px-5 lg:px-8">
        <nav aria-label="Breadcrumb" className="mb-8">
          <ol className="flex flex-wrap gap-2 text-xs tracking-wider text-[var(--text-on-light-muted)]">
            <li>
              <Link href="/" className="hover:text-[var(--pink)]">
                HOME
              </Link>
            </li>
            <li aria-hidden="true">&gt;</li>
            <li className="text-[var(--pink)]">TASKS</li>
          </ol>
        </nav>

        <p className="label-upper mb-3 text-[var(--pink)]">Open Trials</p>
        <h1 className="editorial-heading text-[clamp(2.5rem,5vw,4rem)] text-[var(--text-on-light)]">
          Tasks
        </h1>
        <p className="mt-4 max-w-xl text-sm text-[var(--text-on-light-muted)]">
          Skill-based challenges open to everyone. Pick a task, build your
          solution, and submit before the deadline.
        </p>

        <div className="mt-12 space-y-4">
          {tasks.map((task) => (
            <Link
              key={task.slug}
              href={`/tasks/${task.slug}`}
              className="card-hover group flex flex-col gap-4 border border-[var(--beige)] bg-[var(--cream)] p-6 sm:flex-row sm:items-center sm:justify-between"
            >
              <div>
                <p className="label-upper text-[var(--pink)]">
                  Task {task.number}
                </p>
                <h2 className="editorial-heading mt-2 text-2xl text-[var(--text-on-light)] group-hover:text-[var(--forest)]">
                  {task.title}
                </h2>
                <p className="mt-2 text-sm text-[var(--text-on-light-muted)]">
                  {task.description}
                </p>
              </div>
              <div className="flex flex-col items-start gap-2 sm:items-end">
                <span className="label-upper border border-[var(--tropical)] px-2 py-1 text-[10px] text-[var(--tropical)]">
                  {task.status}
                </span>
                <span className="text-xs text-[var(--text-on-light-muted)]">
                  Deadline: {task.deadline}
                </span>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
