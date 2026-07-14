import { BrowserRouter } from "react-router-dom";
import AppLayout from "@/components/AppLayout";
import { useZoom } from "@/lib/use-zoom";

function AppInner() {
  useZoom();
  return <AppLayout />;
}

export default function App() {
  return (
    <BrowserRouter>
      <AppInner />
    </BrowserRouter>
  );
}
