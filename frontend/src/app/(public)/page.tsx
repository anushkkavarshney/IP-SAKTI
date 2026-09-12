"use client";

import { RedirectIfAuthed } from "../../lib/guards";
import LandingHero from "../../components/LandingHero";
import { HowItWorksSection } from "../../components/HowItWorksFlow";
import LandingFeatures from "../../components/LandingFeatures";
import LandingAbout from "../../components/LandingAbout";
import LandingCta from "../../components/LandingCta";

export default function LandingPage() {
  return (
    <RedirectIfAuthed to="/home">
      <LandingHero />
      <HowItWorksSection />
      <LandingFeatures />
      <LandingAbout />
      <LandingCta />
    </RedirectIfAuthed>
  );
}