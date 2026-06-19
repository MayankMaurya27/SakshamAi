import { motion } from "framer-motion";
import {
  Brain,
  BookOpen,
  FileText,
  CheckCircle,
} from "lucide-react";

export default function WorkspacePreview() {
  return (
    <section className="py-28">

      <div className="max-w-7xl mx-auto px-6">

        <div className="text-center">

          <p className="uppercase tracking-[0.3em] text-sm text-slate-500">
            Learning Workspace
          </p>

          <h2 className="mt-4 text-5xl font-bold text-[#1E3A5F]">
            Designed Around Understanding
          </h2>

        </div>

        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="
            mt-20
            bg-white
            border
            border-slate-200
            rounded-[40px]
            shadow-2xl
            overflow-hidden
          "
        >

          <div className="border-b px-8 py-5 bg-slate-50">

            <div className="flex gap-2">

              <div className="w-3 h-3 rounded-full bg-red-400" />
              <div className="w-3 h-3 rounded-full bg-yellow-400" />
              <div className="w-3 h-3 rounded-full bg-green-400" />

            </div>

          </div>

          <div className="grid lg:grid-cols-[280px_1fr]">

            <div className="border-r p-6 bg-slate-50">

              <h3 className="font-bold text-lg mb-6">
                Learning Tools
              </h3>

              <div className="space-y-4">

                <div className="flex gap-3 items-center">
                  <BookOpen size={20} />
                  Explain
                </div>

                <div className="flex gap-3 items-center">
                  <Brain size={20} />
                  Quiz
                </div>

                <div className="flex gap-3 items-center">
                  <FileText size={20} />
                  Revision
                </div>

              </div>

            </div>

            <div className="p-8">

              <div className="bg-slate-100 rounded-2xl p-4">
                What is Photosynthesis?
              </div>

              <div className="mt-6 bg-blue-50 rounded-2xl p-6">

                <h4 className="font-bold text-lg">
                  Explanation
                </h4>

                <p className="mt-3 text-slate-600">
                  Plants convert sunlight,
                  water and carbon dioxide
                  into food and energy.
                </p>

              </div>

              <div className="grid md:grid-cols-2 gap-5 mt-6">

                <div className="bg-green-50 p-5 rounded-2xl">

                  <h4 className="font-semibold">
                    Key Concepts
                  </h4>

                  <ul className="mt-3 space-y-2">

                    <li>Sunlight</li>
                    <li>Chlorophyll</li>
                    <li>Energy</li>

                  </ul>

                </div>

                <div className="bg-yellow-50 p-5 rounded-2xl">

                  <h4 className="font-semibold">
                    Quick Quiz
                  </h4>

                  <p className="mt-3">
                    Test understanding instantly.
                  </p>

                </div>

              </div>

              <button
                className="
                  mt-6
                  flex
                  items-center
                  gap-2
                  bg-[#1E3A5F]
                  text-white
                  px-5
                  py-3
                  rounded-xl
                "
              >
                <CheckCircle size={18} />
                Save Revision Card
              </button>

            </div>

          </div>

        </motion.div>

      </div>

    </section>
  );
}