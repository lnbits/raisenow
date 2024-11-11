const mapraisenow = (obj) => {
  obj.date = Quasar.utils.date.formatDate(
    new Date(obj.time * 1000),
    "YYYY-MM-DD HH:mm",
  );
  obj.raisenow = ["/raisenow/", obj.id].join("");
  return obj;
};
const mapparticipants = (obj) => {
  obj.date = Quasar.utils.date.formatDate(
    new Date(obj.time * 1000),
    "YYYY-MM-DD HH:mm",
  );
  obj.participants = ["/participants/", obj.id].join("");
  return obj;
};
window.app = Vue.createApp({
  el: "#vue",
  mixins: [windowMixin],
  data: function () {
    return {
      invoiceAmount: 10,
      qrValue: "lnurlpay",
      ranow: [],
      participants: [],
      ranowTable: {
        columns: [
          { name: "id", align: "left", label: "ID", field: "id" },
          { name: "name", align: "left", label: "Name", field: "name" },
          {
            name: "wallet",
            align: "left",
            label: "Wallet",
            field: "wallet",
          },
          { name: "total", align: "left", label: "Total", field: "total" },
        ],
        pagination: {
          rowsPerPage: 10,
        },
      },
      particpantsTable: {
        columns: [
          { name: "id", align: "left", label: "ID", field: "id" },
          { name: "name", align: "left", label: "Name", field: "name" },
          { name: "total", align: "left", label: "Total", field: "total" },
        ],
        pagination: {
          rowsPerPage: 10,
        },
      },
      RaiseFormDialog: {
        show: false,
        data: {},
        advanced_time: false,
      },
      ParticpantsFormDialog: {
        show: false,
        data: {},
      },
      urlDialog: {
        show: false,
        data: {},
      },
    };
  },
  methods: {
    ///////////////// Raises ///////////////////
    exportCSV() {
      LNbits.utils.exportCSV(this.satspotsTable.columns, this.satspots);
    },
    async closeRaiseFormDialog() {
      this.RaiseFormDialog.show = false;
      this.RaiseFormDialog.data = {};
      this.RaiseFormDialog.advanced_time = false;
    },
    async getraisenows() {
      await LNbits.api
        .request("GET", "/raisenow/api/v1/ranow", this.g.user.wallets[0].inkey)
        .then((response) => {
          if (response.data != null) {
            this.ranow = response.data;
          }
          console.log(this.ranow);
        })
        .catch((err) => {
          LNbits.utils.notifyApiError(err);
        });
    },
    async sendraisenowData() {
      if (this.RaiseFormDialog.data.live_dates) {
        this.RaiseFormDialog.data.live_dates = String(
          this.RaiseFormDialog.data.live_dates.from +
            "," +
            this.RaiseFormDialog.data.live_dates.to,
        );
      }
      const wallet = _.findWhere(this.g.user.wallets, {
        id: this.RaiseFormDialog.data.wallet,
      });
      if (this.RaiseFormDialog.data.id) {
        this.updateraisenow(wallet, this.RaiseFormDialog.data);
      } else {
        console.log(this.RaiseFormDialog.data);
        this.createraisenow(wallet, this.RaiseFormDialog.data);
      }
    },
    async updateraisenowForm(tempId) {
      const raisenow = _.findWhere(this.ranow, { id: tempId });
      this.RaiseFormDialog.data = {
        ...raisenow,
      };
      if (raisenow.live_dates) {
        this.RaiseFormDialog.data.live_dates = {
          from: raisenow.live_dates.split(",")[0],
          to: raisenow.live_dates.split(",")[1],
        };
        this.RaiseFormDialog.advanced_time = true;
      }
      console.log(this.RaiseFormDialog.data);
      this.RaiseFormDialog.show = true;
    },
    async createraisenow(wallet, data) {
      await LNbits.api
        .request("POST", "/raisenow/api/v1/ranow", wallet.adminkey, data)
        .then((response) => {
          this.ranow = response.data.map(mapraisenow);
          this.closeRaiseFormDialog();
        })
        .catch((error) => {
          LNbits.utils.notifyApiError(error);
        });
    },
    async updateraisenow(wallet, data) {
      await LNbits.api
        .request("PUT", `/raisenow/api/v1/ranow`, wallet.adminkey, data)
        .then((response) => {
          this.ranow = _.reject(this.ranow, (obj) => {
            return obj.id == data.id;
          });
          this.ranow.push(response.data);
          console.log(this.ranow);
          this.closeRaiseFormDialog();
        })
        .catch((error) => {
          LNbits.utils.notifyApiError(error);
        });
    },
    async deleteraisenow(tempId) {
      let raisenow = _.findWhere(this.ranow, { id: tempId });

      await LNbits.utils
        .confirmDialog("Are you sure you want to delete this raisenow?")
        .onOk(function () {
          LNbits.api
            .request(
              "DELETE",
              "/raisenow/api/v1/ranow/" + tempId,
              _.findWhere(this.g.user.wallets, { id: raisenow.wallet })
                .adminkey,
            )
            .then(function (response) {
              this.ranow = _.reject(this.ranow, function (obj) {
                return obj.id == tempId;
              });
            })
            .catch(function (error) {
              LNbits.utils.notifyApiError(error);
            });
        });
    },
    async exportCSV() {
      await LNbits.utils.exportCSV(this.ranowTable.columns, this.ranow);
    },
    async openRaiseFormDialog(id) {
      const [tempId, itemId] = id.split(":");
      const raisenow = _.findWhere(this.ranow, { id: tempId });
      if (itemId) {
        const item = raisenow.participantsMap.get(id);
        this.RaiseFormDialog.data = {
          ...item,
          raisenow: tempId,
        };
      } else {
        this.RaiseFormDialog.data.raisenow = tempId;
      }
      this.RaiseFormDialog.data.currency = raisenow.currency;
      this.RaiseFormDialog.show = true;
    },
    async closeRaiseFormDialog() {
      this.RaiseFormDialog.show = false;
      this.RaiseFormDialog.data = {};
    },
    async openUrlDialog(id) {
      this.urlDialog.data = _.findWhere(this.ranow, { id });
      this.urlDialog.data = _.findWhere(this.participants, { id });
      this.qrValue = this.urlDialog.data.lnurlpay;
      this.connectWebocket(this.urlDialog.data.id);
      this.urlDialog.show = true;
    },
    ///////////////// Participants ///////////////////
    async getparticipants(raID) {
      await LNbits.api
        .request("GET", "/raisenow/api/v1/participants/" + raID)
        .then((response) => {
          if (response.data != null) {
            this.participants = response.data;
          }
          console.log(this.participants);
        })
        .catch((error) => {
          LNbits.utils.notifyApiError(error);
        });
    },
    async openParticipantDialog(raisenow) {
      this.ParticpantsFormDialog.data = {
        raisenow: raisenow.id,
        wallet: raisenow.wallet,
      };
      this.ParticpantsFormDialog.show = true;
    },
    async updateParticipantForm(tempId, raisenow) {
      const participant = _.findWhere(this.participants, { id: tempId });
      this.ParticpantsFormDialog.data = {
        ...participant,
        raisenow: raisenow.id,
        wallet: raisenow.wallet,
      };
      this.ParticpantsFormDialog.show = true;
    },
    async closeParticpantsFormDialog() {
      this.ParticpantsFormDialog.show = false;
      this.ParticpantsFormDialog.data = {};
    },
    async sendParticipantData() {
      const wallet = _.findWhere(this.g.user.wallets, {
        id: this.ParticpantsFormDialog.data.wallet,
      });
      if (this.ParticpantsFormDialog.data.id) {
        await this.updateParticipant(wallet, this.ParticpantsFormDialog.data);
      } else {
        await this.createParticipant(wallet, this.ParticpantsFormDialog.data);
      }
    },
    async createParticipant(wallet, data) {
      await LNbits.api
        .request("POST", "/raisenow/api/v1/participant", wallet.adminkey, data)
        .then((response) => {
          this.participants = response.data.map(mapparticipants);
          this.closeParticpantsFormDialog();
        })
        .catch((error) => {
          LNbits.utils.notifyApiError(error);
        });
    },
    async updateParticipant(wallet, data) {
      await LNbits.api
        .request("PUT", `/raisenow/api/v1/participant`, wallet.adminkey, data)
        .then((response) => {
          this.participants = _.reject(this.participants, (obj) => {
            return obj.id == data.id;
          });
          this.participants.push(response.data);
          this.closeParticpantsFormDialog();
        })
        .catch((error) => {
          LNbits.utils.notifyApiError(error);
        });
    },
    async deleteAllParticipants(participantId) {
      let raisenow = _.findWhere(this.participants, { id: participantId });

      await LNbits.utils
        .confirmDialog("Are you sure you want to delete all participants?")
        .onOk(function () {
          let wallet = _.findWhere(this.g.user.wallets, {
            id: raisenow.wallet,
          });
          LNbits.api
            .request(
              "DELETE",
              "/raisenow/api/v1/ranow/" + participantId + "/participants",
              wallet.adminkey,
            )
            .then(function (response) {
              this.ranow = _.reject(this.ranow, function (obj) {
                return obj.id == participantId;
              });
            })
            .catch(function (error) {
              LNbits.utils.notifyApiError(error);
            });
        });
    },
    async deleteParticipant(participantId) {
      let participant = _.findWhere(this.participants, { id: participantId });
      let raisenow = _.findWhere(this.ranow, { id: participant.raisenow });
      await LNbits.utils
        .confirmDialog("Are you sure you want to delete this participant?")
        .onOk(function () {
          LNbits.api
            .request(
              "DELETE",
              "/raisenow/api/v1/participant/" + participantId,
              _.findWhere(this.g.user.wallets, { id: raisenow.wallet })
                .adminkey,
            )
            .then(function (response) {
              this.participants = _.reject(this.participants, function (obj) {
                return obj.id == participantId;
              });
            })
            .catch(function (error) {
              LNbits.utils.notifyApiError(error);
            });
        });
    },
    async participantArray(partId) {
      partiipants = this.participants.filter(function (obj) {
        return obj.raisenow == partId;
      });
      console.log(partiipants);
    },
    async handleClick(id, props) {
      this.getparticipants(id);
      props.expand = !props.expand;
    },
    async makeItRain() {
      document.getElementById("vue").disabled = true;
      let end = Date.now() + 2 * 1000;
      let colors = ["#FFD700", "#ffffff"];
      function frame() {
        confetti({
          particleCount: 2,
          angle: 60,
          spread: 55,
          origin: { x: 0 },
          colors: colors,
          zIndex: 999999,
        });
        confetti({
          particleCount: 2,
          angle: 120,
          spread: 55,
          origin: { x: 1 },
          colors: colors,
          zIndex: 999999,
        });
        if (Date.now() < end) {
          requestAnimationFrame(frame);
        } else {
          document.getElementById("vue").disabled = false;
        }
      }
      frame();
    },
    async connectWebocket(wallet_id) {
      if (location.protocol !== "http:") {
        localUrl =
          "wss://" +
          document.domain +
          ":" +
          location.port +
          "/api/v1/ws/" +
          wallet_id;
      } else {
        localUrl =
          "ws://" +
          document.domain +
          ":" +
          location.port +
          "/api/v1/ws/" +
          wallet_id;
      }
      this.connection = new WebSocket(localUrl);
      this.connection.onmessage = function (e) {
        this.makeItRain();
      };
    },
  },
  async created() {
    await this.getraisenows();
  },
});
