"""校验可供分析的资料关系。"""

import unittest

from scripts.inspect_sources import read_table


class SourceContractTest(unittest.TestCase):
    def test_source_observations_and_references(self):
        runs = read_table("runs")
        self.assertGreaterEqual(len({row["recorded"] for row in runs}), 8)
        self.assertTrue(all(0 <= row["wait_min"] < row["working_min"] for row in runs))
        slots = {row["slot"] for row in read_table("mentor_slots")}
        self.assertTrue(all(row["lesson"] in slots for row in runs))
        qualifications = [row for row in read_table("qualifications") if row["qualification"]=="Q11"]
        self.assertEqual([row["state"] for row in qualifications], ["合格","降级"])
        started = [row for row in read_table("schedule") if row["state"] == "已开工"]
        self.assertTrue(any(row["shop"] == qualifications[0]["shop"] and
                            row["fixture"] == qualifications[0]["tooling"] and
                            qualifications[0]["checked"] <= row["day"] < qualifications[1]["checked"] for row in started))

    def test_handover_inputs(self):
        sources = [read_table(name) for name in ['tool_moves', 'customer_receipts', 'recovery_claims', 'schedule']]
        self.assertTrue(all(x["booking"] in {b["booking"] for b in sources[3]} for x in sources[1]))
        self.assertEqual({x["kind"] for x in sources[0] if x["item"]=="FX-001"},
                         {"已发出","到站待确认","已领用","回切申请"})
        self.assertEqual({x["state"] for x in sources[2] if x["tool"]=="FX-001"},{"已接受","提出"})

