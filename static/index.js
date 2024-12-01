window.app = Vue.createApp({
  el: "#vue",
  mixins: [windowMixin],
  data: function () {
    return {
      invoiceAmount: 10,
      qrValue: "lnurlpay",
      ranow: [],
      participants: {
        data: [],
      },
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
      participantsTable: {
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
      ParticipantsFormDialog: {
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
            for (const raisenow of this.ranow) {
              this.getparticipants(raisenow.id);
            }
          }
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
      this.RaiseFormDialog.show = true;
    },
    async createraisenow(wallet, data) {
      await LNbits.api
        .request("POST", "/raisenow/api/v1/ranow", wallet.adminkey, data)
        .then((response) => {
          this.ranow.push(response.data);
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
      this.urlDialog.data = _.findWhere(this.participants.data, { id });
      this.qrValue = this.urlDialog.data.lnurlpay;
      this.connectWebocket(this.urlDialog.data.id);
      this.urlDialog.show = true;
    },
    ///////////////// Participants ///////////////////

    participantArray(value) {
      const participants = this.participants.data
        .map((obj) => Object.assign({}, obj))
        .filter(function (obj) {
          return obj.raisenow == value;
        });

      return participants;
    },
    async getparticipants(raID) {
      await LNbits.api
        .request("GET", "/raisenow/api/v1/participants/" + raID)
        .then((response) => {
          if (response.data != null) {
            this.participants.data.push(...response.data);
          }
        })
        .catch((error) => {
          LNbits.utils.notifyApiError(error);
        });
    },
    async openParticipantDialog(raisenow) {
      this.ParticipantsFormDialog.data = {
        raisenow: raisenow.id,
        wallet: raisenow.wallet,
      };
      this.ParticipantsFormDialog.show = true;
    },
    async updateParticipantForm(tempId, raisenow) {
      const participant = _.findWhere(this.participants.data, { id: tempId });
      this.ParticipantsFormDialog.data = {
        ...participant,
        raisenow: raisenow.id,
        wallet: raisenow.wallet,
      };
      this.ParticipantsFormDialog.show = true;
    },
    async closeParticipantsFormDialog() {
      this.ParticipantsFormDialog.show = false;
      this.ParticipantsFormDialog.data = {};
    },
    async sendParticipantData() {
      const wallet = _.findWhere(this.g.user.wallets, {
        id: this.ParticipantsFormDialog.data.wallet,
      });
      if (this.ParticipantsFormDialog.data.id) {
        await this.updateParticipant(wallet, this.ParticipantsFormDialog.data);
      } else {
        await this.createParticipant(wallet, this.ParticipantsFormDialog.data);
      }
    },
    async createParticipant(wallet, data) {
      await LNbits.api
        .request("POST", "/raisenow/api/v1/participant", wallet.adminkey, data)
        .then((response) => {
          this.participants.data.push(response.data);
          this.closeParticipantsFormDialog();
        })
        .catch((error) => {
          LNbits.utils.notifyApiError(error);
        });
    },
    async updateParticipant(wallet, data) {
      await LNbits.api
        .request("PUT", `/raisenow/api/v1/participant`, wallet.adminkey, data)
        .then((response) => {
          this.participants.data = _.reject(this.participants.data, (obj) => {
            return obj.id == data.id;
          });
          this.participants.data.push(response.data);
          this.closeParticipantsFormDialog();
        })
        .catch((error) => {
          LNbits.utils.notifyApiError(error);
        });
    },
    async deleteAllParticipants(participantId) {
      let raisenow = _.findWhere(this.participants.data, { id: participantId });

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
      let participant = _.findWhere(this.participants.data, {
        id: participantId,
      });
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
              this.participants.data = _.reject(
                this.participants.data,
                function (obj) {
                  return obj.id == participantId;
                },
              );
            })
            .catch(function (error) {
              LNbits.utils.notifyApiError(error);
            });
        });
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
