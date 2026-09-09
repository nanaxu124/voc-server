(() => {
  if (window.Chart) return;

  function px(v, d = 0) { return Number.isFinite(Number(v)) ? Number(v) : d; }

  class ChartFallback {
    constructor(ctx, config) {
      this.ctx = ctx;
      this.canvas = ctx.canvas;
      this.config = config || {};
      this._resize = () => this.draw();
      window.addEventListener('resize', this._resize);
      this.draw();
    }

    destroy() {
      window.removeEventListener('resize', this._resize);
      const {ctx, canvas} = this;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
    }

    draw() {
      const {ctx, canvas, config} = this;
      const rect = canvas.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;
      const width = Math.max(320, Math.floor(rect.width || canvas.parentElement?.clientWidth || 800));
      const height = Math.max(180, Math.floor(rect.height || canvas.parentElement?.clientHeight || 260));
      canvas.width = width * dpr;
      canvas.height = height * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, width, height);

      const labels = config.data?.labels || [];
      const datasets = config.data?.datasets || [];
      const left = 32, right = 18, top = 26, bottom = 34;
      const plotW = Math.max(1, width - left - right);
      const plotH = Math.max(1, height - top - bottom);

      ctx.font = '11px -apple-system, BlinkMacSystemFont, sans-serif';
      ctx.fillStyle = '#86868b';
      ctx.strokeStyle = 'rgba(0,0,0,.08)';
      ctx.lineWidth = 1;

      labels.forEach((label, i) => {
        const x = left + (labels.length <= 1 ? plotW / 2 : i * plotW / (labels.length - 1));
        ctx.textAlign = 'center';
        ctx.fillText(String(label), x, height - 10);
      });

      if (config.type === 'bar') {
        const stacked = !!config.options?.scales?.x?.stacked || !!config.options?.scales?.y?.stacked;
        let max = 1;
        if (stacked) {
          for (let i = 0; i < labels.length; i++) {
            max = Math.max(max, datasets.reduce((s, ds) => s + px(ds.data?.[i]), 0));
          }
        } else {
          datasets.forEach(ds => (ds.data || []).forEach(v => max = Math.max(max, px(v))));
        }

        for (let g = 0; g <= 4; g++) {
          const y = top + plotH * g / 4;
          ctx.beginPath(); ctx.moveTo(left, y); ctx.lineTo(left + plotW, y); ctx.stroke();
        }

        const slot = plotW / Math.max(labels.length, 1);
        const barW = Math.min(44, slot * 0.42);
        labels.forEach((_, i) => {
          let acc = 0;
          datasets.forEach((ds, di) => {
            const val = px(ds.data?.[i]);
            const h = val / max * plotH;
            const x = left + slot * i + slot / 2 - barW / 2;
            const y = top + plotH - h - (stacked ? acc : 0);
            ctx.fillStyle = ds.backgroundColor || (di ? '#af52de' : '#0071e3');
            ctx.fillRect(x, y, barW, h);
            if (stacked) acc += h;
          });
        });

        let lx = left;
        datasets.forEach(ds => {
          ctx.fillStyle = ds.backgroundColor || '#0071e3';
          ctx.fillRect(lx, 7, 10, 10);
          ctx.fillStyle = '#1d1d1f';
          ctx.textAlign = 'left';
          ctx.fillText(ds.label || '', lx + 15, 16);
          lx += 90;
        });
        return;
      }

      let max = 1;
      datasets.forEach(ds => (ds.data || []).forEach(v => max = Math.max(max, px(v))));
      datasets.forEach((ds, di) => {
        const vals = ds.data || [];
        ctx.strokeStyle = ds.borderColor || (di ? '#8e8e93' : '#0071e3');
        ctx.lineWidth = px(ds.borderWidth, 2);
        ctx.beginPath();
        vals.forEach((v, i) => {
          const x = left + (vals.length <= 1 ? plotW / 2 : i * plotW / (vals.length - 1));
          const y = top + plotH - px(v) / max * plotH;
          if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
        });
        ctx.stroke();
        vals.forEach((v, i) => {
          const x = left + (vals.length <= 1 ? plotW / 2 : i * plotW / (vals.length - 1));
          const y = top + plotH - px(v) / max * plotH;
          ctx.fillStyle = ds.borderColor || (di ? '#8e8e93' : '#0071e3');
          ctx.beginPath(); ctx.arc(x, y, 3.5, 0, Math.PI * 2); ctx.fill();
        });
      });
    }
  }

  window.Chart = ChartFallback;
})();