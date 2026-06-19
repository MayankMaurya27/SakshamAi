import MainLayout from "../../components/layout/MainLayout";

import HeroSection from "../../components/learning/HeroSection";
import LearningModes from "../../components/learning/LearningModes";
import WorkspacePreview from "../../components/learning/WorkspacePreview";
import AccessibilitySection from "../../components/learning/AccessibilitySection";

export default function Home() {
  return (
    <MainLayout>

      <HeroSection />

      <LearningModes />

      <WorkspacePreview />

      <AccessibilitySection />

    </MainLayout>
  );
}