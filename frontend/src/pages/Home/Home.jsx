import MainLayout from "../../components/layout/MainLayout";

import HeroSection from "../../components/learning/HeroSection";
import LearningModes from "../../components/learning/LearningModes";
import WorkspacePreview from "../../components/learning/WorkspacePreview";
import AccessibilitySection from "../../components/learning/AccessibilitySection";
import LearningJourney from "../../components/learning/LearningJourney"
import KnowledgeBackground from "../../components/background/KnowledgeBackground";
export default function Home() {
  return (
    <MainLayout>
      <KnowledgeBackground/>
      <HeroSection />
      <WorkspacePreview />
      <LearningModes />
      <AccessibilitySection />
      <LearningJourney />
    </MainLayout>
  );
}
