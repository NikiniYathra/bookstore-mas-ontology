import { FormEvent, useState } from "react";
import { useRunStepMutation, useResetMutation } from "@/lib/query";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Input } from "./ui/input";
import { Button } from "./ui/button";

export function Controls() {
  const [steps, setSteps] = useState(1);
  const [cadence, setCadence] = useState<number | undefined>();
  const [seed, setSeed] = useState<number | undefined>();
  const [message, setMessage] = useState<string | null>(null);

  const runStepMutation = useRunStepMutation();
  const resetMutation = useResetMutation();

  const handleRunStep = async (e: FormEvent) => {
    e.preventDefault();
    setMessage(null);
    try {
      await runStepMutation.mutateAsync({
        steps,
        reasoner_sync_interval: cadence ?? null,
        random_seed: seed ?? null,
      });
      setMessage(`Advanced simulation by ${steps} step${steps > 1 ? "s" : ""}.`);
    } catch (err) {
      setMessage((err as Error).message);
    }
  };

  const handleReset = async () => {
    setMessage(null);
    try {
      await resetMutation.mutateAsync(undefined);
      setMessage("Simulation reset to persisted ontology state.");
    } catch (err) {
      setMessage((err as Error).message);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Simulation Controls</CardTitle>
      </CardHeader>
      <CardContent>
        <form className="grid gap-4 md:grid-cols-4" onSubmit={handleRunStep}>
          <div className="space-y-2">
            <label className="text-xs uppercase text-slate-400">Steps</label>
            <Input
              type="number"
              min={1}
              value={steps}
              onChange={(e) => setSteps(Number(e.target.value))}
            />
          </div>
          <div className="space-y-2">
            <label className="text-xs uppercase text-slate-400">Reasoner cadence</label>
            <Input
              type="number"
              min={1}
              placeholder="Optional"
              value={cadence ?? ""}
              onChange={(e) => setCadence(e.target.value ? Number(e.target.value) : undefined)}
            />
          </div>
          <div className="space-y-2">
            <label className="text-xs uppercase text-slate-400">Random seed</label>
            <Input
              type="number"
              placeholder="Optional"
              value={seed ?? ""}
              onChange={(e) => setSeed(e.target.value ? Number(e.target.value) : undefined)}
            />
          </div>
          <div className="flex items-end gap-2">
            <Button
              type="submit"
              className="w-full"
              disabled={runStepMutation.isPending}
            >
              {runStepMutation.isPending ? "Running…" : "Run Step"}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={handleReset}
              disabled={resetMutation.isPending}
            >
              {resetMutation.isPending ? "Resetting…" : "Reset"}
            </Button>
          </div>
        </form>
        {message && (
          <p className="mt-3 text-sm text-slate-300">{message}</p>
        )}
      </CardContent>
    </Card>
  );
}
