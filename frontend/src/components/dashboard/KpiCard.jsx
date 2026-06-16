


import Card from "../ui/Card";

export default function KpiCard({ label, value, icon }) {
  return (
    <Card className="flex items-center gap-4">

      {icon && <div className="text-xl">{icon}</div>}

      <div>
        <div className="text-sm text-gray-500">{label}</div>
        <div className="text-xl font-semibold">{value}</div>
      </div>

    </Card>
  );
}