import { IconDownload } from "./LineIcons";

const resources = [
  { title: "Starter Kit", description: "Download" },
  { title: "Sample Dataset", description: "Download" },
  { title: "Evaluation Script", description: "Download" },
];

export default function ResourceCards() {
  return (
    <div>
      <h3 className="label-upper mb-4 text-xs font-bold tracking-wider text-[#073523] uppercase">
        Resources
      </h3>
      <div className="grid gap-4 sm:grid-cols-3">
        {resources.map((resource) => (
          <a
            key={resource.title}
            href="#"
            className="group flex items-center justify-between rounded-xl border border-[#E5D7B5] bg-[#FFFDF8] p-5 shadow-sm transition-all duration-200 hover:-translate-y-1 hover:border-[#1C7D47]/40"
          >
            <div>
              <p className="text-sm font-bold text-[#073523]">
                {resource.title}
              </p>
              <p className="mt-1 text-xs font-medium text-[#7A6B4E]">
                {resource.description}
              </p>
            </div>
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#073523]/5 text-[#073523] transition-colors group-hover:bg-[#E60067]/10 group-hover:text-[#E60067]">
              <IconDownload className="h-4 w-4 stroke-[2]" />
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}
