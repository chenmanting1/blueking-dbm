export default class FixpointLog {
  backupinfo: string;
  databases: string[];
  databases_ignore: string[];
  rollback_time: string;
  rollback_type: string;
  source_cluster: {
    id: number;
    immute_domain: string;
    name: string;
  };
  tables: string[];
  tables_ignore: string[];
  target_cluster: {
    cluster_id: number;
    nodes: {
      remote_hosts: {
        bk_biz_id: number;
        bk_cloud_id: number;
        bk_host_id: number;
        ip: string;
      }[];
      spider_host: {
        bk_biz_id: number;
        bk_cloud_id: number;
        bk_host_id: number;
        ip: string;
      };
    };
    operations: {
      cluster_id: number;
      flow_id: number;
      operator: number;
      status: string;
      ticket_id: number;
      ticket_type: string;
      title: string;
    }[];
    phase: string;
    status: string;
  };
  ticket_id: number;

  constructor(payload = {} as FixpointLog) {
    this.backupinfo = payload.backupinfo;
    this.databases = payload.databases || [];
    this.databases_ignore = payload.databases_ignore || [];
    this.rollback_time = payload.rollback_time;
    this.rollback_type = payload.rollback_type;
    this.source_cluster = payload.source_cluster || {};
    this.tables = payload.tables || [];
    this.tables_ignore = payload.tables_ignore || [];
    this.target_cluster = payload.target_cluster || {};
    this.ticket_id = payload.ticket_id;
  }

  get ipText() {
    const ipSet = new Set();
    if (this.target_cluster.nodes.remote_hosts) {
      this.target_cluster.nodes.remote_hosts.forEach((item) => {
        ipSet.add(item.ip);
        ipSet.add(item.ip);
      });
    }
    if (this.target_cluster.nodes.spider_host) {
      ipSet.add(this.target_cluster.nodes.spider_host.ip);
    }
    return [...ipSet].join(' , ');
  }

  get rollbackTypeText() {
    if (this.rollback_type === 'REMOTE_AND_TIME') {
      return `回档到指定时间（${this.rollback_time}）`;
    }
    return `备份记录（${this.backupinfo}）`;
  }

  get isDestoryEnable() {
    return this.target_cluster.phase === 'online';
  }
}
