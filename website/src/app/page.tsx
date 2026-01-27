import Navbar from '@/components/Navbar';
import Hero from '@/components/Hero';
import PipelineFlow from '@/components/visualizer/PipelineFlow';
import Comparison from '@/components/Comparison';
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
        <PipelineFlow />
        <CTA />
        <CodeList />
      </main>
      <Footer />
    </>
  );
}
