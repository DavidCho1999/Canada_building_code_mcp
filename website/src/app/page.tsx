import Navbar from '@/components/Navbar';
import Hero from '@/components/Hero';
import Comparison from '@/components/Comparison';
import HowItWorks from '@/components/HowItWorks';
import Demo from '@/components/Demo';
import CodeList from '@/components/CodeList';
import CTA from '@/components/CTA';
import Footer from '@/components/Footer';

export default function Home() {
  return (
    <>
      <Navbar />
      <main>
        <Hero />
        <Comparison />
        <HowItWorks />
        <CTA />
        <Demo />
        <CodeList />
      </main>
      <Footer />
    </>
  );
}
