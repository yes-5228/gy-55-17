import { AlertTriangle, PackagePlus, RefreshCw } from "lucide-react";
import React, { useEffect, useMemo, useState } from "react";

import { lockersApi, parcelsApi } from "../api/modules";
import DataTable from "../components/DataTable";
import MessageBox from "../components/MessageBox";
import PageHeader from "../components/PageHeader";
import StatusBadge from "../components/StatusBadge";

const initialForm = {
  tracking_no: "",
  sender_name: "",
  receiver_name: "",
  receiver_phone: "",
  carrier: "顺丰",
  size: "medium",
  cell_type: "normal",
  note: "",
};

export default function InboundPage() {
  const [form, setForm] = useState(initialForm);
  const [parcels, setParcels] = useState([]);
  const [cells, setCells] = useState([]);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const loadParcels = () => parcelsApi.list().then(setParcels);
  const loadCells = () => lockersApi.list().then(setCells);

  useEffect(() => {
    loadParcels();
    loadCells();
  }, []);

  const updateField = (event) => {
    setForm({ ...form, [event.target.name]: event.target.value });
  };

  const sizeLabelMap = { small: "小号", medium: "中号", large: "大号" };
  const typeLabelMap = { normal: "普通", refrigerated: "冷藏" };

  const filteredBySelection = useMemo(() => {
    return cells.filter(
      (c) => c.cell_type === form.cell_type && c.size === form.size && c.status === "empty"
    );
  }, [cells, form.cell_type, form.size]);

  const availableBySelection = useMemo(() => {
    return filteredBySelection.filter((c) => !c.is_temperature_alert);
  }, [filteredBySelection]);

  const alertBySelection = useMemo(() => {
    return cells.filter(
      (c) => c.cell_type === form.cell_type && c.is_temperature_alert
    );
  }, [cells, form.cell_type]);

  const isDisabled = useMemo(() => {
    return availableBySelection.length === 0;
  }, [availableBySelection]);

  const tipMessage = useMemo(() => {
    const sizeLabel = sizeLabelMap[form.size];
    const typeLabel = typeLabelMap[form.cell_type];
    if (filteredBySelection.length === 0) {
      return { type: "error", text: `没有空闲的${sizeLabel}${typeLabel}柜格。` };
    }
    if (form.cell_type === "refrigerated" && availableBySelection.length === 0) {
      return {
        type: "error",
        text: `${sizeLabel}冷藏柜温度异常，暂无可用于入库的${sizeLabel}冷藏柜格。`,
      };
    }
    if (form.cell_type === "refrigerated" && alertBySelection.length > 0) {
      return {
        type: "info",
        text: `当前有 ${alertBySelection.length} 个${typeLabel}柜温度异常。`,
      };
    }
    return null;
  }, [form.cell_type, form.size, filteredBySelection, availableBySelection, alertBySelection]);

  const submit = async (event) => {
    event.preventDefault();
    setMessage("");
    setError("");
    try {
      const created = await parcelsApi.inbound(form);
      setMessage(`入库成功，柜格 ${created.locker_cell_detail.code}，取件码 ${created.pickup_code}。`);
      setForm(initialForm);
      loadParcels();
      loadCells();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <>
      <PageHeader title="快件入库" description="登记快件后自动分配空柜格，并生成取件码与通知记录。" />
      <section className="work-grid">
        <form className="panel form-panel" onSubmit={submit}>
          <h2>入库登记</h2>
          <label>运单号<input name="tracking_no" value={form.tracking_no} onChange={updateField} required /></label>
          <label>寄件方<input name="sender_name" value={form.sender_name} onChange={updateField} required /></label>
          <label>收件人<input name="receiver_name" value={form.receiver_name} onChange={updateField} required /></label>
          <label>手机号<input name="receiver_phone" value={form.receiver_phone} onChange={updateField} required /></label>
          <label>承运商<input name="carrier" value={form.carrier} onChange={updateField} required /></label>
          <label>
            柜格尺寸
            <select name="size" value={form.size} onChange={updateField}>
              <option value="small">小</option>
              <option value="medium">中</option>
              <option value="large">大</option>
            </select>
          </label>
          <label>
            柜格类型
            <select name="cell_type" value={form.cell_type} onChange={updateField}>
              <option value="normal">普通</option>
              <option value="refrigerated">冷藏</option>
            </select>
          </label>
          {tipMessage && (
            <div className={`message ${tipMessage.type}`}>
              <AlertTriangle size={16} />
              {tipMessage.text}
            </div>
          )}
          <label>备注<input name="note" value={form.note} onChange={updateField} /></label>
          <button type="submit" disabled={isDisabled}>
            <PackagePlus size={18} />
            {isDisabled ? "暂无可用柜格" : "确认入库"}
          </button>
          <MessageBox type="success">{message}</MessageBox>
          <MessageBox type="error">{error}</MessageBox>
        </form>
        <section className="panel">
          <div className="panel-title">
            <h2>快件列表</h2>
            <button className="ghost" onClick={loadParcels}><RefreshCw size={16} />刷新</button>
          </div>
          <DataTable
            rows={parcels}
            columns={[
              { key: "tracking_no", title: "运单号" },
              { key: "receiver_name", title: "收件人" },
              { key: "cell", title: "柜格", render: (row) => row.locker_cell_detail?.code },
              { key: "type", title: "类型", render: (row) => (
                <StatusBadge
                  status={row.locker_cell_detail?.cell_type}
                  label={row.locker_cell_detail?.cell_type_label}
                />
              )},
              { key: "pickup_code", title: "取件码" },
              { key: "status", title: "状态", render: (row) => <StatusBadge status={row.status} label={row.status_label} /> },
            ]}
          />
        </section>
      </section>
    </>
  );
}
