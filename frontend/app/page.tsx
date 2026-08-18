import Hero from "@/components/Hero";
import ChallengeFeatures from "@/components/ChallengeFeatures";
import BuildingSection from "@/components/BuildingSection";
import Timeline from "@/components/Timeline";
import NoticeBoard from "@/components/NoticeBoard";
import Leaderboard from "@/components/Leaderboard";
import FAQ from "@/components/FAQ";

export default function Home() {
  return (
    <>
      <Hero />
      <ChallengeFeatures />
      <BuildingSection />
      <Timeline />
      <NoticeBoard />
      <Leaderboard />
      <FAQ />
    </>
  );
}
