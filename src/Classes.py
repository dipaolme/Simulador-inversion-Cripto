from Config import rank_percent


class Token():

    def __init__(self, name_, rank, price, market_cap, id_, cluster, amount=0):

        self.name = id_
        self.nombre = name_
        self.price = price
        self.market_cap = market_cap
        self.cmk_rank = rank
        self.amount = amount
        self.operacion = ''
        self.variacion = 0
        self.cluster = cluster

        # agrego variables para testing
        self.new_amount = 0
        self.percent_amount = 0
        self.fondo_asignado = 0
        self.percent_fondo = 0

        self.rank_percent = rank_percent

    def token_amount(self, fondos, new_token_amount=False):
        self.percent_fondo = self.rank_percent[self.cluster][self.cmk_rank]
        fondo_asignado = self.rank_percent[self.cluster][self.cmk_rank] * fondos
        self.fondo_asignado = fondo_asignado
        amount = fondo_asignado / self.price
        if new_token_amount:
            return amount
        else:
            self.amount += amount
            self.operacion = 'compra'

    def mkt_value(self):
        market_value = self.amount * self.price

        self.market_value = market_value

        return market_value

    def comprar(self, amount):
        self.amount += amount
        self.variacion = amount
        self.operacion = 'compra'

    def vender(self, amount):
        self.amount -= amount
        self.variacion = -amount
        self.operacion = 'venta'


class Cluster():

    def __init__(self, name, fondos_cluster, fondos_bal, tolerancia_balanceo, tokens, first_day=False):

        self.name = name
        self.tokens = tokens
        self.tolerancia_balanceo = tolerancia_balanceo
        self.costo_operacion = 0
        self.fondos_cluster = fondos_cluster
        self.fondos_bal = fondos_bal

        if first_day:
            self.transacciones = len(self.tokens)
        else:
            self.transacciones = 0

    def mkt_value(self):

        market_value = 0

        for t in self.tokens:
            market_value += t.price * t.amount

        return market_value

    def new_token_amount(self):
        for t in self.tokens:
            new_amount = t.token_amount(
                self.fondos_cluster, new_token_amount=True)
            # testing
            t.new_amount = new_amount
            if t.amount != 0:
                percent_amount = new_amount / t.amount - 1
                # testing
                t.percent_amount = percent_amount

                if percent_amount > self.tolerancia_balanceo:
                    # buy_amount = percent_amount * t.amount
                    buy_amount = new_amount - t.amount
                    t.comprar(buy_amount)
                    self.transacciones += 1
                    self.costo_operacion += (t.amount * t.price) * 0.001
                    self.fondos_bal -= (t.amount * t.price) * 0.001

                elif percent_amount < -self.tolerancia_balanceo:
                    sell_amount = -percent_amount * t.amount
                    t.vender(sell_amount)
                    self.transacciones += 1
                    self.costo_operacion += (t.amount * t.price) * 0.001
                    self.fondos_bal -= (t.amount * t.price) * 0.001

                else:
                    if percent_amount > 0:
                        self.fondos_bal += (new_amount - t.amount) * t.price
                    elif percent_amount < 0:
                        self.fondos_bal -= (-percent_amount *
                                            t.amount) * t.price

            else:
                buy_amount = new_amount
                t.comprar(buy_amount)
                self.transacciones += 1
                self.costo_operacion += (t.amount * t.price) * 0.001
                self.fondos_bal -= (t.amount * t.price) * 0.001
